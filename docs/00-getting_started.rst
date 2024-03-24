:og:description: Get started with mantelo.

.. meta::
   :description: Get started with mantelo.

.. _getting_started:

🏁 Getting started
====================


To get started, install the package:

.. code-block:: python

    pip install mantelo

Now, assuming you have a Keycloak Server running, what's left is to:

1. authenticate to Keycloak, :ref:`authentication`
2. make calls, see :ref:`making_calls`

For a quick test drive, use the
`docker-compose.yml <https://github.com/derlin/mantelo/blob/main/docker-compose.yml>`_ included in
the repo and start a Keycloak server locally using ``docker compose up``. Open a Python REPL and
type:

.. code-block:: python

    from mantelo import KeycloakAdmin

    # We assume the server is running on localhost:9090
    # and the admin user is "admin" with password "admin"
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

