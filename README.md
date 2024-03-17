# CAPE: A Keycloak Admin REST Api Client for Python

[![codecov](https://codecov.io/gh/derlin/cape/graph/badge.svg?token=5Y2O7B7342)](https://codecov.io/gh/derlin/cape)
![PyPI - Python Version](https://img.shields.io/pypi/v/cape)

---

**✨✨ CAPE is a super small yet super powerful tool for interacting with the Keycloak Admin API ✨✨**

It stays always **fresh** and **complete** because it does not implement or wrap any endpoint.
Instead, it offers an object-oriented interface to the Keycloak ReSTful API. Acting as a wrapper
around the well-known [requests](https://requests.readthedocs.io/en/latest/) library and using
slumber under the hood, it abstracts all the boring stuff such as authentication (tokens and refresh
tokens), URL handling, serialization, and the processing of requests. This magic is made possible by
the excellent [slumber](https://slumber.readthedocs.io/) library.

⮕ Any endpoint your Keycloak supports, CAPE supports!

---

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [🚀 Why CAPE?](#-why-cape)
- [🏁 Getting started](#-getting-started)
- [🔐 Authenticate to Keycloak](#-authenticate-to-keycloak)
  - [Authenticating with username+password](#authenticating-with-usernamepassword)
  - [Authenticating with a service account (client ID + secret)](#authenticating-with-a-service-account-client-id--secret)
  - [Other ways of authenticating](#other-ways-of-authenticating)
- [📡 Making calls](#-making-calls)
- [💀 Exceptions](#-exceptions)

<!-- TOC end -->

---

## 🚀 Why CAPE?

- CAPE only relies on 3 small packages.
- Contrary to other libraries such as
  [python-keycloak](https://python-keycloak.readthedocs.io/en/latest/), CAPE is always up-to-date
  and doesn't lack any endpoints.
- CAPE makes your code look nice and object-oriented, instead of having long hard-coded URL strings everywhere.
- CAPE abstracts away authentication (and refresh tokens), which is always tricky to get right.
- CAPE gives you access to the exact URL that was called, and the `requests.Response` in case of error,
  so debugging is easy.
- CAPE is flexible: you can tweak it easily if you need to.

## 🏁 Getting started

To get started, install the package:

```bash
pip install cape
```

Now, assuming you have a Keycloak Server running, you need to:

1. authenticate, see [🔐 Authenticate to Keycloak](#-authenticate-to-keycloak)
2. make calls, see [📡 Making calls](#-making-calls)

## 🔐 Authenticate to Keycloak

To authenticate to Keycloak, you can either use a username+password, or a service account (client
ID+client secret).

The library takes care of fetching a token the first time you need it and keeping it fresh. By
default, it tries to use the refresh token (if available) and always guarantees the token is valid
for the next 30s.

**IMPORTANT** A client is meant to interact with a single realm, which can be different
from the realm used for authentication.

### Authenticating with username+password

Ensure your user has the right to interact with the endpoints you are interested in.
In doubt or for testing, you can either use the admin user (not recommended) or create
a user and assign it the `realm-management:realm-admin` role (full access).

The default client `admin-cli` can always be used for connection.

Here is how to connect to the default realm with the admin user and `admin-cli` client:

```python
from cape import KeycloakAdmin

client = KeycloakAdmin.from_credentials(
    server_url="http://localhost:8080", # base Keycloak URL
    realm_name="master",
    # ↓↓ Authentication
    client_id="admin-cli",
    username="admin",
    password="CHANGE-ME", # TODO
)
```

This client will be able to make calls only to the `master` realm.
If you want to authenticate to a realm that is different from the one
you want to query, use the argument `authentication_realm`:

```python
from cape import KeycloakAdmin

client = KeycloakAdmin.from_credentials(
    server_url="http://localhost:8080", # base Keycloak URL
    realm_name="my-realm", # realm for querying
    # ↓↓ Authentication
    authentication_realm_name="admin", # realm for authentication only
    client_id="admin-cli",
    username="admin",
    password="CHANGE-ME",
)
```

### Authenticating with a service account (client ID + secret)

To authenticate via a client, the latter needs:

- to have "Client authentication" enabled,
- to support the `Service accounts roles` authentication flow,
- to have one or more service account roles granting access to Admin endpoints.

Go to your client's "Credentials" tab to find the client secret.

Here is how to connect with a client:

```python
from cape import KeycloakAdmin

client = KeycloakAdmin.from_service_account(
    server_url="http://localhost:8080", # base Keycloak URL
    realm_name="master",
    # ↓↓ Authentication
    client_id="my-client-name",
    client_secret="59c3c211-2e56-4bb8-a07d-2961958f6185",
)
```

This client will be able to make calls only to the `master` realm.
If you want to authenticate to a realm that is different from the one
you want to query, use the argument `authentication_realm`:

```python
from cape import KeycloakAdmin

client = KeycloakAdmin.from_service_account(
    server_url="http://localhost:8080", # base Keycloak URL
    realm_name="my-realm", # realm for querying
    # ↓↓ Authentication
    authentication_realm_name="admin", # realm for authentication only
    client_id="my-client-name",
    client_secret="59c3c211-2e56-4bb8-a07d-2961958f6185",
)
```

### Other ways of authenticating

The supported authentication methods should be enough. If you need more, a pull request or an issue
is welcome! But just in case, here are some ways to make it more complicated 😉.

To create a `KeycloakAdmin`, you only need a method that returns a token. For example, you can use
an existing token directly (not recommended, as tokens are short-lived):

```python
from cape.client import BearerAuth, KeycloakAdmin

KeycloakAdmin(
    server_url="http://localhost:8080"
    realm_name="master",
    auth=BearerAuth(lambda: "my-token"),
)
```

If you want to go further, you can create your own `Connection` class (or extend the
`OpenidConnection`), and pass its `.token` method to the `BearerAuth`:

```python
from cape.client import BearerAuth, KeycloakAdmin

connection = Connection(...)

KeycloakAdmin(
    server_url="http://localhost:8080"
    realm_name="master",
    auth=BearerAuth(connection.token),
)
```

## 📡 Making calls

Once you have configured how to authenticate to Keycloak, the rest is easy-peasy.
CAPE **starts with the URL `<server-url>/admin/realms/<realm-name>`** and constructs
the URL from there, depending on how you call the client.

The return value is the HTTP response content, parsed from JSON. In case of error, an
`HttpException` with access to the raw response is available (see [💀 Exceptions](#-exceptions)).

Query parameters can be passed as `kwargs` to `.get`, `.post`, etc.
`.post` and `.put` take the payload as first argument, or as the named argument `data`.

Here are some examples of URL mapping (`c` is the `KeycloakAdmin` object):

| call                                                    | URL                                                                             |
| ------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `c.users.get()`                                         | `GET /admin/realms/{realm}/users`                                               |
| `c.users.get(max=1)`                                    | `GET /admin/realms/{realm}/users?max=1`                                         |
| `c.users.count.get()`                                   | `GET /admin/realms/{realm}/users/count`                                         |
| `c.users("725209cd-9076-417b-a404-149a3fb8e35b").get()` | `GET /admin/realms/{realm}/users/725209cd-9076-417b-a404-149a3fb8e35b`          |
| `c.users.post({"username": ...})`                       | `POST /admin/realms/{realm}/users/725209cd-9076-417b-a404-149a3fb8e35b`         |
| `c.users.post(foo=bar, data={"username": ...})`         | `POST /admin/realms/{realm}/users/725209cd-9076-417b-a404-149a3fb8e35b?foo=bar` |

Here are some examples:

```python
>> client.users.get()
[{'id': '8d83ecda-766d-4382-8f3a-4c5ac1962961',
  'username': 'constant',
  'firstName': 'Jasper',
  'lastName': 'Fforde',
  'email': 'j@f.uk',
  'emailVerified': True,
  'createdTimestamp': 1710273159287,
  'enabled': True,
  'totp': False,
  'disableableCredentialTypes': [],
  'requiredActions': [],
  'notBefore': 0,
  'access': {'manageGroupMembership': True,
   'view': True,
   'mapRoles': True,
   'impersonate': False,
   'manage': True}}]

>> client.users.count.get()
2

>> c.clients.get()
...
HttpException: (403, {'error': 'unknown_error', 'error_description': 'For more on this error consult the server log at the debug level.'}, 'http://localhost:9090/admin/realms/orwell/clients', <Response [403]>)
```

## 💀 Exceptions

If an error occurs during _authentication_, CAPE will raise an `AuthenticationException` with the
`error` and `errorDescription` from Keycloak. All other exceptions are instances of `HttpException`.

Here are some examples:

```python
# Using an inexistant client
AuthenticationException(
    error='invalid_client',
    error_description='Invalid client or Invalid client credentials'
)

# Trying to access an endpoint without the proper permissions
HttpException(
    status_code=403,
    json={'error': 'unknown_error', 'error_description': 'For more on this error consult the server log at the debug level.'},
    url='http://localhost:9090/admin/realms/orwell/clients',
    response='<requests.Response>',
)
```
