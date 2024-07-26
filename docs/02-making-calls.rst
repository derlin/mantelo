:og:description: How to make calls to the Keycloak Admin API using mantelo.

.. meta::
   :description: How to make calls to the Keycloak Admin API using mantelo.

.. _making_calls:

📡 Making calls
===============

General overview
----------------

Once you have configured how to authenticate to Keycloak, the rest is easy-peasy. mantelo **starts
with the URL** ``<server-url>/admin/realms/<realm-name>`` and constructs the URL from there,
depending on how you call the client.

The return value is the HTTP response content as a :python:`dict` (parsed from the JSON response). In
case of error, an :py:class:`~.HttpException` with access to the raw response is available.

All the calls in the chain are used to generate the URL, except for the last call which determines the HTTP method to use.
Supported HTTP methods are:

* :python:`.get(**kwargs)`
* :python:`.options(**kwargs)`
* :python:`.head(**kwargs)`
* :python:`.post(data=None, files=None, **kwargs)`
* :python:`.patch(data=None, files=None, **kwargs)`
* :python:`.put(data=None, files=None, **kwargs)`
* :python:`.delete(**kwargs)`

The ``kwargs`` are used to add query parameters to the URL. The ``data`` and ``files`` parameters
are used to add a payload to the request. See :py:meth:`requests.Session.request` for more
information on the allowed values for these parameters.


To better understand, here are some examples of URL mapping (``c`` is the
:py:class:`~.KeycloakAdmin` object):

* :python:`c.users.get()` translates to::
    
    GET /admin/realms/{realm}/users 

* :python:`c.users.get(search="foo bar")` translates to::
    
    GET /admin/realms/{realm}/users?search=foo+bar

* :python:`c.users.count.get()` translates to::
        
    GET /admin/realms/{realm}/users/count

* :python:`c.users("725209cd-9076-417b-a404-149a3fb8e35b").get()` translates to
   
  .. code-block:: none
      
    GET /admin/realms/{realm}/users/725209cd-9076-417b-a404-149a3fb8e35b


* :python:`c.users.post({"username": ...})` translates to
        
  .. code-block:: none

    POST /admin/realms/{realm}/users/725209cd-9076-417b-a404-149a3fb8e35b

    > Content-Type: application/json
    > {"username": ...}

* :python:`c.users.post(foo=1, data={"username": ...})` translates to
        
  .. code-block:: none

    POST /admin/realms/{realm}/users?foo=1

    > Content-Type: application/json
    > {"username": ...}

Special case: working with realms
---------------------------------


By default, a client is bound to a realm, and has the base URL set to
``<server-url>/admin/realms/<realm-name>``. Hence, to query ``GET /admin/realms/<realm-name>``, you
can use :python:`c.get()` directly (or :python:`c.post({})` to update its properties).

.. important::

    Be careful not to delete the realm you used for authentication, as it will invalidate your token!
    :python:`c.delete()` should be avoided if you used the same realm for connection and the client.

Remember that you can switch the realm by setting the :py:attr:`~.KeycloakAdmin.realm_name`
attribute. This will only change the base URL (the result of the calls), not the connection itself.
You will stay logged in to the initial realm you connected with.

If you want to work with the ``/realms/`` endpoint itself, for instance, to list all realms, or
create a new one, you can use the special :py:attr:`~.KeycloakAdmin.realms` attribute on the client.
It returns a slumber resource whose base URL is ``<server-url>/admin/realms`` (without any realm
name). The same rules apply as for the other resources, but the URL is now relative to the
``/realms/`` endpoint. For example, you can list realms with :python:`c.realms.get()`.

See :ref:`examples` for more hands-on examples.
