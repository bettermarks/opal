SHELL := /bin/bash

.PHONY: k8s_synth
k8s_synth:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run synth)

.PHONY: k8s_install
k8s_install:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm ci)

.PHONY: k8s_test
k8s_test:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run test)

.PHONY: k8s_test_update
k8s_test_update:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run test -- -u)

.PHONY: k8s_pretty
k8s_pretty:
	(cd k8s && source ${HOME}/.nvm/nvm.sh && nvm use && npm run prettier)

.PHONY: init
init:
	kubectl create namespace licensing || true
	skaffold run --cleanup=false --profile init

.PHONY: run-api
run-api:
	skaffold dev --profile run-api

.PHONY: create-db
create-db:
	skaffold run --cleanup=false --profile create-db

.PHONY: pg-port-forward
pg-port-forward:
	kubectl port-forward service/licensing-db 5433:5432 -n licensing

.PHONY: run-migration
run-migration:
	skaffold run --cleanup=false --profile run-migration

.PHONY: run-event-export
run-event-export:
	skaffold run --cleanup=false --profile run-event-export

.PHONY: start
start:
	make init
	make create-db
	make run-migration
	kubectl wait --for=condition=complete --timeout=120s --namespace=licensing job/licensing-migration
	make run-event-export
	make run-api

.PHONY: delete
delete:
	skaffold delete -p init
	skaffold delete -p run-api
	skaffold delete -p create-db
	skaffold delete -p run-event-export