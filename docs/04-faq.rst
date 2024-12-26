:og:description: Answers to some mantelo user questions.

.. meta::
   :description: Answers to some mantelo user questions.


.. _faq:

📢 FAQ
======

.. testsetup:: *

    from mantelo import KeycloakAdmin
    from uuid import uuid4, UUID
    import requests

    client = KeycloakAdmin.from_username_password(
           server_url="http://localhost:9090",
           realm_name="master",
           client_id="admin-cli",
           username="admin",
           password="admin",
    )


Can I connect to Keycloak if it uses a self-signed certificate?
---------------------------------------------------------------

Mantelo uses a :py:class:`requests.Session` object to make the HTTP requests. You can pass a custom
session when creating a :py:class:`~.KeycloakAdmin` object. This allows you to set the
:py:attr:`~requests.Session.verify` parameter to ``False`` to ignore the certificate validation, or
to specify the path to a custom certificate bundle.

Here is an example:

.. code:: python

    from mantelo import KeycloakAdmin
    import requests

    # Create the session and customize it as you like
    # Note: the authentication part will be added by mantelo
    session = requests.Session()
    session.verify = False  # or "/path/to/ca-bundle.crt" for a custom certificate

    client = KeycloakAdmin.from_username_password(
        # Usual connection information
        server_url="https://localhost:8080",
        realm_name="master",
        client_id="admin-cli",
        username="admin",
        password="admin", 
        # ↓↓ Custom session
        session=session,  # <= here is the trick!
    )

More info can be found requests documentation, for example `SSL Cert Verification
<https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification>`_.


Can I get the raw response object from the server?
--------------------------------------------------

Getting the raw response is especially useful for some create endpoints that return the UUID of the
created resource only in the ``location`` headers.

.. note:: 
    
    When an exception occurs, the raw response is always available in the exception object
    (see :py:attr:`.HttpException.response` attribute).

By default, mantelo always parses the body of the response and returns it as a dictionary. To change
this behavior, simply call the :py:meth:`~.Resource.as_raw` method *anywhere* in the chain. This will
make mantelo return a tuple instead, with the raw :py:class:`requests.Response` as the first
element. The second element is the decoded content.

To make it clearer, here is an example:

.. testcode::

    ## This is the regular behavior
    decoded = client.groups.get()

    ## This let you access the raw response
    (raw_response, decoded) = client.groups.as_raw().get()

    assert(isinstance(raw_response, requests.Response))

A good example where this is useful is to get the UUID of the newly created resource,
as Keycloak currently does not return it but mentions it in the ``location`` header.

.. testcode::

    ## Create a new group
    (resp, _) = client.as_raw().groups.post({"name": f"my-group-{uuid4()}"})
    
    ## get the UUID of the new group from the location header
    loc = resp.headers["location"]
    # -> 'http://localhost:9090/admin/realms/my-realm/groups/73a2abf9-3797-433f-99c6-304fa4b2c961'
    uuid = UUID(loc.split("/")[-1])
    # -> UUID('73a2abf9-3797-433f-99c6-304fa4b2c961')


Note that the ``as_raw()`` can really be placed anywhere before the final HTTP call, so
``client.as_raw().groups.get()`` is equivalent to ``client.groups.as_raw().get()``. Choose your
style!


More questions?
---------------

Don't hesitate to create an `issue <https://github.com/derlin/mantelo/issues/new>`_, I will be happy
to help you!
