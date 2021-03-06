
# default target does nothing
.DEFAULT_GOAL: default
default: ;

init:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
.PHONY: init

start:
	docker run --rm -d -p "8000:8000" --name stellar zulucrypto/stellar-integration-test-network
	sleep 5
.PHONY: start

stop:
	docker stop stellar
.PHONY: stop

testnet:
	python -m pytest -v -rs --cov=kin -s -x test --testnet
.PHONY: testnet

test:
	python -m pytest -v -rs --cov=kin -s -x test
.PHONY: test

wheel:
	python setup.py bdist_wheel
.PHONY: wheel

pypi:
	twine upload dist/*
.PHONY: pypi

clean:
	rm -f .coverage
	find . -name \*.pyc -delete
.PHONY: clean
