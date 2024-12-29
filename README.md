# mantelo: A Keycloak Admin REST Api Client for Python

[![codecov](https://codecov.io/gh/derlin/mantelo/graph/badge.svg?token=5Y2O7B7342)](https://codecov.io/gh/derlin/mantelo)
[![PyPI](https://img.shields.io/pypi/v/mantelo)](https://pypi.org/project/mantelo/)
![PyPI Downloads](https://static.pepy.tech/badge/mantelo)
[![Documentation Status](https://readthedocs.org/projects/mantelo/badge/?version=latest)](https://mantelo.readthedocs.io/en/latest/?badge=latest)
---

<img src="https://github.com/derlin/mantelo/blob/main/docs/_static/images/mantelo-text-900.png" alt="Mantelo" width="500">

**✨✨ MANTELO is a super small yet super powerful library for interacting with the Keycloak Admin API ✨✨**

> Mantelo [manˈtelo], from German "*Mantel*", from Late Latin "*mantum*" means "*cloak*" in Esperanto.

It stays fresh and complete because it does not hard-code or wrap any endpoint. Instead, Instead, it
offers a clean, object-oriented interface to the Keycloak RESTful API. Acting as a lightweight
wrapper around the popular [requests](https://requests.readthedocs.io/en/latest/) library, mantelo
takes care of all the boring details for you - like authentication (tokens and refresh tokens), URL
management, serialization, and request processing

Any endpoint your Keycloak supports, mantelo supports!

> [!TIP]
> Read more in the ${{\color{Gold}\huge\text{full documentation}}}\$ at https://mantelo.readthedocs.io/en/latest/

---

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [🚀 Why mantelo?](#-why-mantelo)
- [🏁 Getting started](#-getting-started)
- [🔐 Authenticate to Keycloak](#-authenticate-to-keycloak)
   * [Authenticating with username+password](#authenticating-with-usernamepassword)
   * [Authenticating with client credentials (client ID + secret)](#authenticating-with-client-credentials-client-id--secret)
   * [Other ways of authenticating](#other-ways-of-authenticating)
- [📡 Making calls](#-making-calls)
- [💀 Exceptions](#-exceptions)

<!-- TOC end -->

---

## 🚀 Why mantelo?

You may ask why using mantelo instead of writing your own requests wrapper, or another library such
as [python-keycloak](https://python-keycloak.readthedocs.io/en/latest/). Here are some
(non-exhaustive) arguments to help you make the right choice:

- mantelo only relies on 2 small packages (`requests` and `attrs`).
- Contrary to other libraries such as python-keycloak, mantelo is always up-to-date and doesn't lack
  any endpoints.
- mantelo makes your code look nice and promotes a clean, object-oriented approach, avoiding
  hard-coded URL strings scattered throughout your code.
- mantelo abstracts away authentication (and refresh tokens), which is always tricky to get right.
- mantelo gives you access to the exact URL that was called, and the `requests.Response` in case of
  error, making debugging easier.
- mantelo is flexible: you can tweak it easily if you need to.

## 🏁 Getting started

To get started, install the package:

```bash
pip install mantelo
```

Now, assuming you have a Keycloak Server running, what's left is to:

1. authenticate, see [🔐 Authenticate to Keycloak](#-authenticate-to-keycloak)
2. make calls, see [📡 Making calls](#-making-calls)

For a quick test drive, use the [docker-compose.yml](docker-compose.yml) included in this repo and
start a Keycloak server locally using `docker compose up`. Open a Python REPL and type:

```python
from mantelo import KeycloakAdmin

c = KeycloakAdmin.from_username_password(
    server_url="http://localhost:9090",
    realm_name="master",
    client_id="admin-cli",
    username="admin",
    password="admin",
)

# get the list of clients in realm "master"
c.clients.get()

# create a user
c.users.post({
    "username": "test",
    "enabled": True,
    "credentials": [{"type": "password", "value": "test"}],
})
# get the user id
c.users.get(username="test")[0]["id"]

# ...
```

## 🔐 Authenticate to Keycloak

To authenticate to Keycloak, you can either use a username+password, or client credentials (client
ID+client secret, also known as *service account*).

The library takes care of fetching a token the first time you need it and keeping it fresh. By
default, it tries to use the refresh token (if available) and always guarantees the token is valid
for the next 30 seconds.

> [!IMPORTANT]
> A client is meant to interact with a single realm, which can be different
> from the realm used for authentication.

### Authenticating with username+password

Ensure your user has the right to interact with the endpoint(s) you are interested in. In doubt or
for testing, you can either use the admin user (not recommended) or create a user and assign it the
`realm-management:realm-admin` role (full access).

The default client `admin-cli` can always be used for connection.

Here is how to connect to the default realm with the admin user and `admin-cli` client:

```python
from mantelo import KeycloakAdmin

client = KeycloakAdmin.from_username_password(
    server_url="http://localhost:8080", # base Keycloak URL
    realm_name="master",
    # ↓↓ Authentication
    client_id="admin-cli",
    username="admin",
    password="CHANGE-ME", # TODO
)
```

This client will be able to make calls only to the `master` realm. If you want to authenticate to a
realm that is different from the one you want to query, use the argument `authentication_realm`:

```python
from mantelo import KeycloakAdmin

client = KeycloakAdmin.from_username_password(
    server_url="http://localhost:8080", # base Keycloak URL
    realm_name="my-realm", # realm for querying
    # ↓↓ Authentication
    authentication_realm_name="master", # realm for authentication only
    client_id="admin-cli",
    username="admin",
    password="CHANGE-ME",
)
```

### Authenticating with client credentials (client ID + secret)

> [!TIP]
> 
> To authenticate via a client, the latter needs:
> - to have "Client authentication" enabled,
> - to support the `Service accounts roles` authentication flow,
> 
> - to have one or more service account roles granting access to Admin endpoints.
> 
> Go to your client's "Credentials" tab to find the client secret.

Here is how to connect with a client:

```python
from mantelo import KeycloakAdmin

client = KeycloakAdmin.from_client_credentials(
    server_url="http://localhost:8080", # base Keycloak URL
    realm_name="master",
    # ↓↓ Authentication
    client_id="my-client-name",
    client_secret="59c3c211-2e56-4bb8-a07d-2961958f6185",
)
```

This client will be able to make calls only to the `master` realm. If you want to authenticate to a
realm that is different from the one you want to query, use the argument `authentication_realm`:

```python
from mantelo import KeycloakAdmin

client = KeycloakAdmin.from_client_credentials(
    server_url="http://localhost:8080", # base Keycloak URL
    realm_name="my-realm", # realm for querying
    # ↓↓ Authentication
    authentication_realm_name="master", # realm for authentication only
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
from mantelo.client import BearerAuth, KeycloakAdmin

KeycloakAdmin(
    server_url="http://localhost:8080",
    realm_name="master",
    auth=BearerAuth(lambda: "my-token"),
)
```

If you want to go further, you can create your own `Connection` class (or extend the
`OpenidConnection`), and pass its `.token` method to the `BearerAuth`:

```python
from mantelo.client import BearerAuth, KeycloakAdmin
from mantelo.connection import Connection

class MyConnection(Connection):
    def token(self):
        return "<do-something-here>"

connection = MyConnection()

KeycloakAdmin(
    server_url="http://localhost:8080",
    realm_name="master",
    auth=BearerAuth(connection.token),
)
```

## 📡 Making calls

Once you have configured how to authenticate to Keycloak, the rest is easy-peasy. mantelo **starts
with the URL `<server-url>/admin/realms/<realm-name>`** and constructs the URL from there, depending
on how you call the client.

The return value is the HTTP response content, parsed from JSON. In case of error, an
`HttpException` with access to the raw response is available (see [💀 Exceptions](#-exceptions)).

Query parameters can be passed as `kwargs` to `.get`, `.post`, etc. `.post`, `.put`, and `.delete`
take the payload as the first argument, or as the named argument `data`.

Here are some examples of URL mapping (`c` is the `KeycloakAdmin` object):

| call                                                    | URL                                                                           |
| ------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `c.users.get()`                                         | `GET /admin/realms/{realm}/users`                                             |
| `c.users.get(search="foo bar")`                         | `GET /admin/realms/{realm}/users?search=foo+bar`                              |
| `c.users.count.get()`                                   | `GET /admin/realms/{realm}/users/count`                                       |
| `c.users("725209cd-9076-417b-a404-149a3fb8e35b").get()` | `GET /admin/realms/{realm}/users/725209cd-9076-417b-a404-149a3fb8e35b`        |
| `c.users.post({"username": ...})`                       | `POST /admin/realms/{realm}/users/725209cd-9076-417b-a404-149a3fb8e35b`       |
| `c.users.post(foo=1, data={"username": ...})`           | `POST /admin/realms/{realm}/users/725209cd-9076-417b-a404-149a3fb8e35b?foo=1` |


> [!NOTE]
> More examples and explanations are available in the docs: https://mantelo.readthedocs.io/en/latest/02-making-calls.html


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

If the server returns a *401 Unauthorized* during the _authentication_ process, mantelo will raise
an `AuthenticationException` with the `error` and `errorDescription` from Keycloak. All other HTTP
exceptions are instances of `HttpException`, with some subclasses (`HttpNotFound`,
`HttpClientError`, `HttpServerError`).

Here are some examples:

```python
# Using an inexistant client
AuthenticationException(
    error='invalid_client',
    error_description='Invalid client or Invalid client credentials'
    response='<requests.Response>',
)

# Trying to access an endpoint without the proper permissions
HttpException(
    status_code=403,
    json={'error': 'unknown_error', 'error_description': 'For more on this error consult the server log at the debug level.'},
    url='http://localhost:9090/admin/realms/orwell/clients',
    response='<requests.Response>',
)
```

---

Find more in the docs, https://mantelo.readthedocs.io/en/latest/, and don't forget to leave a ⭐ if you enjoy this library!
