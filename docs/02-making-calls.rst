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

All the calls in the chain are used to generate the URL, except for the last call which determines
the HTTP method to use. Supported HTTP methods are (see :py:class:`~.Resource` for more
information):

* :python:`.get(**kwargs)`
* :python:`.options(**kwargs)`
* :python:`.head(**kwargs)`
* :python:`.post(data=None, files=None, **kwargs)`
* :python:`.patch(data=None, files=None, **kwargs)`
* :python:`.put(data=None, files=None, **kwargs)`
* :python:`.delete(data=None, files=None, **kwargs)`

The ``kwargs`` can be used to add query parameters to the URL. The ``data`` and ``files`` parameters
can be used to add a payload to the request. See :py:meth:`requests.Session.request` for more
information on the allowed values for these parameters.

.. note::

    If you have a doubt or want to play with the URL mapping behavior without doing any real call,
    use the special method ``.url()``. It will return the translated URL, with no side effect!

    Spin up a Python shell and try it out right now:

    .. testcode::

        from mantelo import KeycloakAdmin
        c = KeycloakAdmin("https://invalid.com", "my-realm", None)
        url = c.just_trying.some("mapping").url()
        print(url)

    Yields:

    .. testoutput::

        https://invalid.com/admin/realms/my-realm/just-trying/some/mapping

    (Parameters themselves are handled by :py:mod:`requests`).

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

About dashes
------------

Since Python doesn't allow dashes in method names, but Keycloak URLs use them in some places,
Mantelo automatically converts any underscores in method names to dashes in the URL.

In other words, to call:

.. code-block:: none

    GET /admin/realms/{realm}/client-scopes

You can use:

.. code-block:: python

    c.client_scopes.get()

Note that you could also use ``c("client-scopes").get()``, but let's admit it, it is ugly (so
don't).

About the return type of HTTP calls
-----------------------------------

HTTP calls return the JSON response as a Python dictionary, with the following exceptions:

1. When the HTTP method is ``DELETE``, the return value is a boolean indicating success (2xx status
   code) or failure (other status codes).
2. When the response is empty, the return value is an empty string, to match :py:mod:`requests` behavior.
3. When the content-type of the response doesn't match a JSON content-type, mantelo returns the
   response text as a string, or the raw bytes if the body can not be decoded. It does not
   attempt any parsing.

In case of error, an :py:class:`~.HttpException` is raised, with the raw response available in the 
:py:attr:`~HttpException.response` attribute.

Finally, there may be times when you need to access the raw response object. For this, use the
:py:meth:`~.Resource.as_raw` method anywhere in the chain. This will make mantelo return a tuple
instead, with the raw :py:class:`requests.Response` as the first element. The second element is
the decoded content, and follow the same rules as laid above.


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
