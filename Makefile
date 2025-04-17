SHELL := /bin/bash

.PHONY: synth
synth:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run synth)

.PHONY: cdk_install
cdk_install:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm ci)

.PHONY: cdk_test
cdk_test:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run test)

.PHONY: update_snapshots
update_snapshots:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run test -- -u)

.PHONY: cdk_pretty
cdk_pretty:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run prettier)
