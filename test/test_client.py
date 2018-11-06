import pytest
from time import sleep

from kin import KinClient, TEST_ENVIRONMENT, KinErrors
from kin import config


def test_create():
    client = KinClient(TEST_ENVIRONMENT)
    assert client
    assert client.environment == TEST_ENVIRONMENT
    assert client.horizon
    assert client.kin_asset == TEST_ENVIRONMENT.kin_asset
    assert client.network == TEST_ENVIRONMENT.name


def test_get_config(setup, test_client):
    from kin import Environment
    # bad Horizon endpoint
    env = Environment('bad', 'bad', 'bad', 'GDZA33STWFOVWLHAFXEOYS46DA2VMIQH3MCCVVGAUENMZMMZJFAHT4KO')
    status = KinClient(env).get_config()
    assert status['horizon']
    assert status['horizon']['online'] is False
    assert status['horizon']['error'].startswith("Invalid URL 'bad': No schema supplied")

    # no Horizon on endpoint
    env = Environment('bad', 'http://localhost:666', 'bad', 'GDZA33STWFOVWLHAFXEOYS46DA2VMIQH3MCCVVGAUENMZMMZJFAHT4KO')
    status = KinClient(env).get_config()
    assert status['horizon']
    assert status['horizon']['online'] is False
    assert status['horizon']['error'].find('Connection refused') > 0

    # success
    status = test_client.get_config()
    assert status['environment'] == setup.environment.name
    assert status['horizon']
    assert status['horizon']['uri'] == setup.environment.horizon_uri
    assert status['horizon']['online']
    assert status['horizon']['error'] is None
    assert status['transport']
    assert status['transport']['pool_size']
    assert status['transport']['num_retries']
    assert status['transport']['request_timeout']
    assert status['transport']['retry_statuses']
    assert status['transport']['backoff_factor']


def test_get_balance(test_client, test_account):
    balances = test_client.get_account_balances(test_account.get_public_address())
    assert balances['XLM'] > 0
    assert balances['KIN'] > 0


def test_get_account_status(test_client, test_account):
    from kin import AccountStatus

    with pytest.raises(ValueError, match='invalid address: bad'):
        test_client.get_account_status('bad')

    address = 'GB7F23F7235ADJ7T2L4LJZT46LA3256QAXIU56ANKPX5LSAAS3XVA465'
    assert test_client.get_account_status(address) == AccountStatus.NOT_CREATED
    assert test_client.get_account_status(test_client.kin_asset.issuer) == AccountStatus.NOT_ACTIVATED
    assert test_client.get_account_status(test_account.get_public_address()) == AccountStatus.ACTIVATED


def test_get_account_data(test_client, test_account):
    with pytest.raises(ValueError, match='invalid address: bad'):
        test_client.get_account_data('bad')

    address = 'GBSZO2C63WM2DHAH4XGCXDW5VGAM56FBIOGO2KFRSJYP5I4GGCPAVKHW'
    with pytest.raises(KinErrors.AccountNotFoundError):
        test_client.get_account_data(address)

    acc_data = test_client.get_account_data(test_account.get_public_address())
    assert acc_data
    assert acc_data.id == test_account.get_public_address()
    assert acc_data.sequence
    assert acc_data.data == {}

    assert acc_data.thresholds
    assert acc_data.thresholds.low_threshold == 0
    assert acc_data.thresholds.medium_threshold == 0
    assert acc_data.thresholds.high_threshold == 0

    assert acc_data.flags
    assert not acc_data.flags.auth_revocable
    assert not acc_data.flags.auth_required

    assert len(acc_data.balances) == 2
    asset_balance = acc_data.balances[0]
    native_balance = acc_data.balances[1]
    assert asset_balance.balance > 0
    # default limit
    assert asset_balance.limit == 922337203685.4775807
    assert asset_balance.asset_type == 'credit_alphanum4'
    assert asset_balance.asset_code == 'KIN'
    assert asset_balance.asset_issuer == test_client.kin_asset.issuer
    assert native_balance.balance > 0
    assert native_balance.asset_type == 'native'

    # just to increase test coverage
    assert str(acc_data)


def test_get_transaction_data(test_client):
    from kin import OperationTypes
    from kin.transactions import RawTransaction

    with pytest.raises(ValueError, match='invalid transaction hash: bad'):
        test_client.get_transaction_data('bad')

    with pytest.raises(KinErrors.ResourceNotFoundError):
        test_client.get_transaction_data('deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef')

    address = 'GAHTWFVYV4RF2AMEZP3X2VOK4HB3YOSARU7VNVTP7J2OLDSVOP564YEN'
    tx_hash = test_client.friendbot(address)
    sleep(5)
    tx_data = test_client.get_transaction_data(tx_hash)
    assert tx_data
    assert tx_data.id == tx_hash
    assert tx_data.timestamp
    assert tx_data.memo is None
    assert tx_data.operation
    assert tx_data.source == test_client.kin_asset.issuer  # root account
    assert tx_data.operation.type == OperationTypes.CREATE_ACCOUNT
    assert tx_data.operation.destination == address
    assert tx_data.operation.starting_balance == 10

    tx_data = test_client.get_transaction_data(tx_hash, simple=False)
    assert isinstance(tx_data, RawTransaction)


def test_friendbot(test_client):
    from kin import AccountStatus
    address = 'GDIPKVWPVCL5E5MX4UWMLCGXMDWEMEYAZGCI3TPJPVDG5ZFA6VJAA7RA'
    test_client.friendbot(address)
    assert test_client.get_account_status(address) == AccountStatus.NOT_ACTIVATED

    with pytest.raises(ValueError):
        test_client.friendbot('bad')


def test_verify_kin_payment(test_client, test_account):
    address = 'GCZXR4ILXETTNQMUNF54ILRMPEG3UTUUMYKPUXU5633VCOABZZ63H7FJ'
    seed = 'SCJQYWGJTL3NUEJ4H2QRDGQHO4HW3RX4IAZEEUDGLTIE5I4MEFR4UZYZ'
    tx_hash = test_client.friendbot(address)
    sleep(5)

    assert not test_client.verify_kin_payment(tx_hash, 'source', 'destination', 123)

    tx_hash = test_client.activate_account(seed)
    sleep(5)
    assert not test_client.verify_kin_payment(tx_hash, 'source', 'destination', 123)

    tx_hash = test_account.send_kin('GCZXR4ILXETTNQMUNF54ILRMPEG3UTUUMYKPUXU5633VCOABZZ63H7FJ', 123, 'Hello')
    sleep(5)
    assert test_client.verify_kin_payment(tx_hash, test_account.get_public_address(), address, 123)
    assert test_client.verify_kin_payment(tx_hash, test_account.get_public_address(), address, 123, 'Hello', True)


def test_activate_account(test_client):
    from kin import AccountStatus

    seed = 'SBHR6N6GZ5AFDS6JELO2PFDAD5OIABQ4MMWTYNKBGJEDNM5JVPJFG3AF'
    address = 'GA4GDLBEWVT5IZZ6JKR4BF3B6JJX5S6ISFC2QCC7B6ZVZWJDMR77HYP6'

    with pytest.raises(ValueError):
        test_client.activate_account('bad')

    with pytest.raises(KinErrors.AccountNotFoundError):
        test_client.activate_account(seed)

    test_client.friendbot(address)
    test_client.activate_account(seed)
    assert test_client.get_account_status(address) == AccountStatus.ACTIVATED

    with pytest.raises(KinErrors.AccountActivatedError):
        test_client.activate_account(seed)

def test_tx_history(test_client,test_account):
    txs = []
    for _ in range(6):
        txs.append(test_account.send_xlm('GA4GDLBEWVT5IZZ6JKR4BF3B6JJX5S6ISFC2QCC7B6ZVZWJDMR77HYP6',1))

    # let horizon ingest the txs
    sleep(10)
    tx_history = test_client.get_account_tx_history(test_account.get_public_address(), amount=6)

    history_ids = [tx.id for tx in tx_history]
    # tx history goes from latest to oldest
    txs.reverse()

    assert txs == history_ids

    # test paging
    config.MAX_RECORDS_PER_REQUEST = 2

    tx_history = test_client.get_account_tx_history(test_account.get_public_address(), amount=6)
    history_ids = [tx.id for tx in tx_history]

    assert txs == history_ids
