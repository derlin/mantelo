.PHONY: all

default: help

help:
	@awk 'BEGIN {FS = ": .*##";} /^[$$()% 0-9a-zA-Z_-]+(\\:[$$()% 0-9a-zA-Z_-]+)*:.*?##/ { gsub(/\\:/,":", $$1); printf "  \033[36m%-5s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


##@ Build

build: ## Build the wheels and sdist.
	find . -name "*.egg-info" | xargs rm -rf && \
	rm -rf dist && \
	python -m build

##@ Development

lint: ## Run ruff to format and lint (inside docker).
	docker run --rm -e LINT_FOLDER_PYTHON=mantelo -v $(CURDIR):/app divio/lint /bin/lint ${ARGS} --run=python

test: ## Run tests with tox (inside docker).
	coverage erase
	docker compose up -d --wait keycloak
	docker compose run --rm tox ${ARGS}
	coverage combine
	coverage html
	coverage xml

mypy: ## Run mypy locally to check types.
	mypy mantelo

export-realms: ## Export test realms after changes in Keycloak Test Server.
	docker compose exec keycloak /opt/keycloak/bin/kc.sh export --dir /tmp/export --users realm_file; \
    for realm in master orwell; do \
        file=$$realm-realm.json; \
        (docker compose exec keycloak cat /tmp/export/$$file) | \
        jq 'walk(if type == "object" then del(.id) else . end)' | jq --sort-keys \
        > tests/realms/$$file; \
    done
