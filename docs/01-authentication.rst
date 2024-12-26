:og:description: How to authenticate to Keycloak using mantelo.

.. meta::
   :description: How to authenticate to Keycloak using mantelo.

.. _authentication:

🔐 Authenticating to Keycloak
==============================

To authenticate to Keycloak, you can either use a username+password, or client credentials (client
ID+client secret, also known as *service account*).

The library takes care of fetching a token the first time you need it and keeping it fresh. By
default, it tries to use the refresh token (if available) and always guarantees the token is valid
for the next 30 seconds.

The authentication calls and the calls to the REST API use the same :py:class:`requests.Session`,
which can be passed at creation in case you need to add custom headers, proxies, etc.

.. important::

    A :py:class:`~.KeycloakAdmin` client is meant to interact with a single realm. It is however
    possible to use another realm for authentication. You may change realms by setting
    :py:attr:`~.KeycloakAdmin.realm_name`, but this requires your token to have permissions spanning
    realms (e.g. authentication using the admin user).

.. _authentication-password:

Authenticating with username + password
----------------------------------------

Ensure your user has the right to interact with the endpoints you are interested in. In doubt or for
testing, you can either use the admin user (not recommended) or create a user and assign it the
``realm-management:realm-admin`` role (full access).

.. hint::

    Clients must enable the "*Direct access grants*" authorization flow.
    The client ``admin-cli``, which exists by default on all realms, is often used.

Here is how to use :py:meth:`~.KeycloakAdmin.from_username_password` connect to the default realm
with the admin user and ``admin-cli`` client:

.. code:: python

   from mantelo import KeycloakAdmin

   client = KeycloakAdmin.from_username_password(
       server_url="http://localhost:8080", # base Keycloak URL
       realm_name="master",
       # ↓↓ Authentication
       client_id="admin-cli",
       username="admin",
       password="CHANGE-ME", # TODO
   )

This client will be able to make calls only to the ``master`` realm. If you want to authenticate to
a realm that is different from the one you want to query, use the argument ``authentication_realm``:

.. code:: python

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

.. _authenticate-client:

Authenticating with client credentials (client ID + secret)
-----------------------------------------------------------

It is also possible to authenticate through an OIDC client with a confidential access type.

.. hint::

    A confidential client should:

    -  have "*Client authentication*" enabled,
    -  support the "*Service accounts roles*" authentication flow,
    -  have one or more service account roles granting access to Admin endpoints.

    Go to your client's "Credentials" tab to find the client secret.

Here is how to use :py:meth:`~.KeycloakAdmin.from_client_credentials` connect with a client:

.. code:: python

   from mantelo import KeycloakAdmin

   client = KeycloakAdmin.from_client_credentials(
       server_url="http://localhost:8080", # base Keycloak URL
       realm_name="master",
       # ↓↓ Authentication
       client_id="my-client-name",
       client_secret="59c3c211-2e56-4bb8-a07d-2961958f6185",
   )

This client will be able to make calls only to the ``master`` realm. If you want to authenticate to
a realm that is different from the one you want to query, use the argument ``authentication_realm``:

.. code:: python

   from mantelo import KeycloakAdmin

   client = KeycloakAdmin.from_client_credentials(
       server_url="http://localhost:8080", # base Keycloak URL
       realm_name="my-realm", # realm for querying
       # ↓↓ Authentication
       authentication_realm_name="master", # realm for authentication only
       client_id="my-client-name",
       client_secret="59c3c211-2e56-4bb8-a07d-2961958f6185",
   )

Other ways of authenticating
----------------------------

The supported authentication methods should be enough. If you need more, a pull request or an issue
is welcome! But just in case, here are some ways to make it more complicated 😉.

To create a :py:class:`~.KeycloakAdmin`, you only need a method that returns a token. For example,
you can use an existing token directly (not recommended, as tokens are short-lived):

.. code:: python

   from mantelo.client import BearerAuth, KeycloakAdmin

   KeycloakAdmin(
       server_url="http://localhost:8080",
       realm_name="master",
       auth=BearerAuth(lambda: "my-token"),
   )

If you want to go further, you can create your own :py:class:`~.Connection` class (or extend the
:py:class:`~.OpenidConnection`), and pass its :py:meth:`~.OpenidConnection.token` method to the
:py:class:`~.BearerAuth`:

.. code:: python

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
