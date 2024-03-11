.PHONY: lint test setup_build build

lint:
	docker run --rm -it -e LINT_FOLDER_PYTHON=keycloak -v $(CURDIR):/app divio/lint /bin/lint ${ARGS} --run=python

test:
	coverage erase
	docker compose up -d --wait keycloak
	docker compose run --rm tox ${ARGS}
	coverage combine
	coverage html

build:
	find . -name "*.egg-info" | xargs rm -rf && \
	rm -rf dist && \
	python -m build


export-realms: ## Export realms after changes in Keycloak.
	docker compose exec keycloak /opt/keycloak/bin/kc.sh export --dir /tmp/export --users realm_file; \
    for realm in master orwell; do \
        file=$$realm-realm.json; \
        (docker compose exec keycloak cat /tmp/export/$$file) | \
        jq 'walk(if type == "object" then del(.id) else . end)' | jq --sort-keys \
        > tests/realms/$$file; \
    done
