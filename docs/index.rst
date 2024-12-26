:og:description: Mantelo is a super small yet super powerful Python library for interacting with the Keycloak Admin API.

.. meta::
   :description: Mantelo is a super small yet super powerful Python library for interacting with the Keycloak Admin API.

Mantelo: A Keycloak Admin REST Api Client for Python
=====================================================

✨ MANTELO is a super small yet super powerful tool for interacting with the Keycloak Admin API ✨.

   Mantelo [manˈtelo], from German "*Mantel*", from Late Latin "*mantum*" means "*cloak*" in Esperanto.

It always stays **fresh** and **complete** because it does not hard-code or wrap any endpoint.
Instead, Instead, it offers a clean, object-oriented interface to the Keycloak RESTful API. Acting
as a lightweight wrapper around the popular `requests <https://requests.readthedocs.io/en/latest/>`_
library, mantelo takes care of all the boring details for you - like authentication (tokens and
refresh tokens), URL management, serialization, and request processing [#mention]_.

⮕ Any endpoint your Keycloak supports, mantelo supports!

-------------------

.. toctree::
   :maxdepth: 2
   :caption: Contents

   00-getting_started
   01-authentication
   02-making-calls
   03-examples
   04-faq
   90-api

-------------------

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

-------------------

.. [#mention] A big thanks to the excellent `slumber <https://slumber.readthedocs.io/>`_ library, which inspired this project.
