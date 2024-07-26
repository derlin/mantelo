:og:description: Example API calls with Mantelo.

.. meta::
   :description: Example API calls with Mantelo.


.. _examples:

📓 Examples
===========

Assuming you created a client (see :ref:`authentication`), here are some examples of how to interact with the Keycloak Admin API using Mantelo.
Don't hesitate to create an `issue <https://github.com/derlin/mantelo/issues/new/choose>`_ if you want to see more examples or if you have any questions.

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
    b''

    # Get the ID of the newly created user
    >>> user_id = client.users.get(username="test_user")[0]["id"]

    >>> client.users(user_id).get()['username']
    'test_user'

    # Add some password credentials
    >>> client.users(user_id).put({"credentials": [{"type": "password", "value": "CHANGE_ME"}]})

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
