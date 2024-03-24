# 🔧 Contributing

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Prerequisites](#prerequisites)
- [Setting up the environment](#setting-up-the-environment)
- [Running checks and tests](#running-checks-and-tests)
- [About commits](#about-commits)
- [How to contribute](#how-to-contribute)

<!-- TOC end -->

## Prerequisites

Ensure you have the following available on your machine:

- Python
- Docker

## Setting up the environment

To work on this library locally, install the library in edit mode along with the dev dependencies:

```bash
# Use .[dev,test] to also install pytest and related libraries
pip install -e '.[dev]'
```

To spawn the Keycloak Test Server, use the docker-compose.yml (done automatically when running
tests, see blow):
```bash
docker compose up --wait
```

The server is configured using the resources in `tests/realms` and is available at
`http://localhost:9090`. If you need to change anything to the realms, ensure you persist your
changes using `make export-realms`.

## Running checks and tests

A **Makefile** is available for all the usual development tasks. Use `help` to list the available
commands:

```bash
make help
```
```text
Build
  build  Build the wheels and sdist.

Documentation
  docs   Generate the HTML documentation.
  docs-clean  Remove docs build artifacts.
  docs-open  Open the documentation locally (requires make docs to have ran).

Development
  lint   Run ruff to format and lint (inside docker).
  test   Run tests with tox (inside docker).
  mypy   Run mypy locally to check types.
  export-realms  Export test realms after changes in Keycloak Test Server.
```

Note that `make test` automatically starts a Keycloak container if it isn't already running. You may
have to stop it manually. The test server is configured using the resources in `tests/realms` and is
available at `http://localhost:9090`. To start the Keycloak server yourself:

```bash
docker compose up --wait
```

You can run the tests directly using `pytest` for faster development, just ensure you installed the
test dependencies (`pip install -e '.[dev,test]'`) and Keycloak is running.

## About commits

This repository adheres to the
[Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0/) and requires
[signed commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).

## How to contribute

1. Fork this repository, develop and test your changes
2. Make sure that your changes do not decrease the test coverage
3. Create signed commits that follow the conventional commits specification
4. If necessary, update the docs
5. Submit a pull request

