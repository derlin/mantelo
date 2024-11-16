:og:description: Answers to some mantelo user questions.

.. meta::
   :description: Answers to some mantelo user questions.


.. _faq:

📢 FAQ
======

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
of the created resource only in the headers.

.. note:: 
    
    When an exception occurs, the raw response is always available in the exception object
    (see :py:attr:`.HttpException.response` attribute).

By default, mantelo always parses the body of the response and returns it as a dictionary. However,
there is a trick to get the raw response object of any call. In short, every time mantelo does a
request, it stores the raw response in the special ``_`` attribute of the resource. As long as you
keep a reference to the object, you can access the last call's raw response.

To make it clearer, here is an example:

.. code:: python

    ## Keep a reference to the endpoint you which to use
    groups_endpoint = client.groups

    ## Make the call
    groups_endpoint.post({"name": "my-group"})

    ## You can now access the last response's object via `_` attribute:
    groups_endpoint._.headers["location"]
    # 'http://localhost:9090/admin/realms/my-realm/groups/73a2abf9-3797-433f-99c6-304fa4b2c961'
    groups_endpoint._.request.method
    # POST

Note that every time you call e.g. ``client.groups``, you get a new instance. This makes it easy to
parallelize calls without fear of interference: just use different references. To better understand:

.. code:: python

    a = client.users
    b = client.users

    a.get()
    b.get()

    a._ != b._ # each holds its own raw response object
    a.get() # this only updates a._, not b._


More questions?
---------------

Don't hesitate to create an `issue <https://github.com/derlin/mantelo/issues/new>`_, I will be happy
to help you!
