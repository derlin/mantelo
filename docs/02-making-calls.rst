:og:description: How to make calls to the Keycloak Admin API using mantelo.

.. meta::
   :description: How to make calls to the Keycloak Admin API using mantelo.

.. _making_calls:

📡 Making calls
===============

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
