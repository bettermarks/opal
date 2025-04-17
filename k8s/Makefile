# Called from Tiltfile

SHELL := /bin/sh

# ref: tsconfig.json
SRCS_TS = $(shell find . -name node_modules -prune -o -type f -name '*.ts' -print)


.PHONY: all
all: dist

node_modules: package-lock.json
	npm ci

dist: node_modules $(SRCS_TS)
	npm run synth

.PHONY: clean
clean:
	rm -rf dist node_modules
