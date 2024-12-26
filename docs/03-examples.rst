:og:description: Example API calls with Mantelo.

.. meta::
   :description: Example API calls with Mantelo.


.. _examples:

📓 Examples
===========

Assuming you created a client (see :ref:`authentication`), here are some examples of how to interact
with the Keycloak Admin API using Mantelo. Don't hesitate to create an
`issue <https://github.com/derlin/mantelo/issues/new/choose>`_ if you want to see more examples or
if you have any questions.

Create, update, and delete a user
---------------------------------

.. testsetup:: *

    from mantelo import KeycloakAdmin

    client = KeycloakAdmin.from_username_password(
           server_url="http://localhost:9090",
           realm_name="master",
           client_id="admin-cli",
           username="admin",
           password="admin",
    )

    user_id = None


.. doctest::

    # Create a new user
    >>> client.users.post({
    ...    "username": "test_user",
    ...    "email": "user@example.com",
    ...    "enabled": True,
    ...    "emailVerified": True,
    ... })
    ''

    # Get the ID of the newly created user
    >>> user_id = client.users.get(username="test_user")[0]["id"]

    >>> client.users(user_id).get()['username']
    'test_user'

    # Add some password credentials
    >>> client.users(user_id).put({"credentials": [{"type": "password", "value": "CHANGE_ME"}]})
    ''

    >>> client.users(user_id).credentials.get()
    [{'id': ..., 'type': 'password', 'createdDate': ..., 'credentialData': ...}]

    # Delete the user
    >>> client.users(user_id).delete()
    True

List and count resources
-------------------------

.. doctest::

    # Count the number of users
    >>> client.users.count.get()
    1

    # List the first 10 users in the realm
    >>> client.users.get(max=10)
    [{...}]

    # List the next 10 users in the realm (in this case, we don't have any)
    >>> client.users.get(max=10, first=10)
    []

    # List all clients in the realm
    >>> client.clients.get()
    [{...}, {...}, ...]

    # List roles associated with the broker client
    >>> c_uid = client.clients.get(clientId="broker")[0]["id"]
    >>> client.clients(c_uid).roles.get()
    [{'id': ..., 'name': 'read-token', 'description': ..., 'composite': False, 'clientRole': True, 'containerId': ...}]

    # Count the active sessions for a client
    >>> client.clients(c_uid).session_count.get()
    {'count': 0}


Interact with realms directly
-----------------------------

If you need to view or edit properties of the current realm (``/admin/realm/{realm}`` endpoint), you
can use the client directly:

.. doctest::

        # Describe the current realm
        >>> client.get()
        {'id': ..., 'realm': 'master', 'displayName': ..., ...}

        # Update the realm
        >>> client.put({"displayName": "MASTER!"})
        ''

You can at any point change the realm of the client by setting the
:py:attr:`~.KeycloakAdmin.realm_name`. This won't impact the connection, which will still use the
same token. This is useful when you want to switch to another realm definitely. If you only need to
do a few operations in another realm, consider using the :py:attr:`~.KeycloakAdmin.realms` instead
(keep reading).

.. doctest::

    >>> client.get()["realm"]
    'master'

    # Change the realm
    >>> client.realm_name = "orwell"

    # Describe the current realm
    >>> client.get()["realm"]
    'orwell'

    # Switch back to the original realm
    >>> client.realm_name = "master"

To work with the ``/admin/realms/`` endpoint directly, for example, to list existing realms or create a new one,
or simply to quickly query another realm's information, use the special `~.KeycloakAdmin.realms` attribute:

.. doctest::

    # List all realms
    >>> len(client.realms.get())
    2

    # Create a new realm
    >>> client.realms.post({"realm": "new_realm", "enabled": True, "displayName": "New Realm"})
    ''

    # Get the new realm
    >>> client.realms("new_realm").get()
    {'id': ..., 'realm': 'new_realm', 'displayName': 'New Realm', ...}

    # Query the users in the new realm
    >>> client.realms("new_realm").users.get()
    []

    # Delete the new realm
    >>> client.realms("new_realm").delete()
    True
