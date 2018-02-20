# KIN Python SDK for Stellar Blockchain
[![Build Status](https://travis-ci.org/kinfoundation/kin-core-python.svg?branch=master)](https://travis-ci.org/kinfoundation/kin-core-python) [![Coverage Status](https://codecov.io/gh/kinfoundation/kin-core-python/branch/master/graph/badge.svg)](https://codecov.io/gh/kinfoundation/kin-core-python)

## Disclaimer

The SDK is still in beta. No warranties are given, use on your own discretion.

## Requirements.

Make sure you have Python 2 >=2.7.9.

## Installation 

```bash
pip install git+https://github.com/kinfoundation/kin-core-python.git
```

## Usage

### Initialization

To initialize the SDK, you need to provide the following parameters:
- (optional) the seed to init the internal SDK wallet with. If not provided, you will NOT be able to use the 
  following functions: `get_address`, `get_native_balance`, `get_kin_balance`, `create_account`, `monitor_kin_payments`,
  `_trust_asset`, `_send_asset`.
- (optional) the endpoint URI of your [Horizon](https://www.stellar.org/developers/horizon/reference/) node. 
  If not provided, a default Horizon endpoint will be used,either a testnet or pubnet, depending on the `network` 
  parameter below.
- (optional) a network identifier, which is either `PUBLIC` or `TESTNET`, defaults to `PUBLIC`.
- (optional) a list of channel seeds. If provided, the channel accounts will be used to sign transactions instead 
  of the internal SDK wallet.


```python
import kin

# Init SDK without a seed, in the public Stellar network (for generic blockchain queries)
sdk = kin.SDK()

# Init SDK without a seed, for Stellar testnet
sdk = kin.SDK(network='TESTNET')

# Init SDK without a seed, with specific Horizon server, running on Stellar testnet
sdk = kin.SDK(horizon_endpoint_uri='http://my.horizon.uri', network='TESTNET')

# Init SDK with wallet seed, on public network
sdk = kin.SDK(seed='my seed')

# Init SDK with several channels, on public network
sdk = kin.SDK(seed='my seed', channel_seeds=['seed1', 'seed2', ...])
```
For more examples, see the [SDK test file](test/test_sdk.py).


### Getting Wallet Details
```python
# Get the address of my wallet account. The address is derived from the seed the SDK was inited with.
address = sdk.get_address()
```

### Getting Account Balance
```python
# Get native (lumen) balance of the SDK wallet
native_balance = sdk.get_native_balance()

# Get KIN balance of the SDK wallet
kin_balance = sdk.get_kin_balance()

# Get native (lumen) balance of some account
native_balance = sdk.get_account_native_balance('address')

# Get KIN balance of some account
kin_balance = sdk.get_account_kin_balance('address')
```

### Getting Account Data
```python
# returns kin.AccountData
account_data = sdk.get_account_data('address')
```

### Checking If Account Exists
```python
account_exists = sdk.check_account_exists('address')
```

### Creating a New Account
```python
# create a new account prefunded with MIN_ACCOUNT_BALANCE lumens
tx_hash = sdk.create_account('address')

# create a new account prefunded with a specified amount of native currency (lumens).
tx_hash = sdk.create_account('address', starting_balance=1000)
```

### Checking if Account is Activated (Trustline established)
```python
# check if KIN is trusted by some account
kin_trusted = sdk.check_account_activated('address')
```

### Sending Currency
```python
# send native currency (lumens) to some address
tx_hash = sdk.send_native('address', 100, memo_text='order123')

# send KIN to some address
tx_hash = sdk.send_kin('address', 1000, memo_text='order123')
```

### Getting Transaction Data
```python
# create a transaction, for example a new account
tx_hash = sdk.create_account('address')
# get transaction data, returns kin.TransactionData
tx_data = sdk.get_transaction_data(tx_hash)
```

### Transaction Monitoring
```python
# define a callback function that receives an address and a kin.TransactionData object
def print_callback(address, tx_data):
    print(address, tx_data)
    
# start monitoring KIN payments related to the SDK wallet account
sdk.monitor_kin_payments(print_callback)

# start monitoring KIN payments related to a list of addresses
sdk.monitor_accounts_kin_payments(['address1', 'address2'], print_callback)

# start monitoring all transactions related to a list of addresses
sdk.monitor_accounts_transactions(['address1', 'address2'], print_callback)
```

### Helpers
The following functions are specific to Stellar and not part of the high-level API, but they can be handy in 
application development and testing.

```python
from stellar_base.asset import Asset
my_asset = Asset('XYZ', 'asset issuer address')

# Get asset balance of some account
asset_balance = sdk._get_account_asset_balance('address', my_asset)

# check if the asset is trusted by some account
asset_trusted = sdk._check_asset_trusted('address', my_asset)

# establishing a Trustline from SDK wallet to the asset
tx_hash = sdk._trust_asset(my_asset, limit=1000)

# send asset to some address
tx_hash = sdk._send_asset(my_asset, 'address', 100, memo_text='order123')

# monitor asset payments related to a list of accounts
sdk._monitor_accounts_transactions(my_asset, ['address1', 'address2'], print_callback, only_payments=True)
```

## Limitations


## License
The code is currently released under [MIT license](LICENSE).


## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for SDK contributing guidelines. 

