.PHONY: build fmt run clean
ifndef VERBOSE
.SILENT:
endif

build:
	docker-compose -f compose/docker-compose-dev.yml build

fmt:
	black growth scripts

dev-up: build
	docker-compose -f compose/docker-compose-dev.yml up -d
	docker-compose -f compose/docker-compose-dev.yml exec growth bash

dev-down:
	docker-compose -f compose/docker-compose-dev.yml down --remove-orphans

