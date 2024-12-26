from collections.abc import Callable

import requests
from attrs import define, evolve

from .connection import (
    ClientCredentialsConnection,
    OpenidConnection,
    UsernamePasswordConnection,
)
from .internal.api import API, Resource


__all__ = ["BearerAuth", "KeycloakAdmin"]


@define
class BearerAuth(requests.auth.AuthBase):
    """
    An authentication class that uses a Bearer token.

    This requests authentication class adds a Bearer token to the request headers.
    The token is provided by a callable (called for every request).

    :param token_getter: A callable that returns the token to use for authentication.
    """

    token_getter: Callable[[], str]
    """The callable that returns the token to use for authentication."""

    def __call__(
        self, r: requests.PreparedRequest
    ) -> requests.PreparedRequest:
        r.headers["Authorization"] = f"Bearer {self.token_getter()}"
        return r


class KeycloakAdmin(API):
    """
    A client to interact with the Keycloak Admin API.

    Highly inspired by the awesome `slumber <https://slumber.readthedocs.io/en/stable/>`_ library,
    KeycloakAdmin is a lightweight object offering a more Pythonic interface to the Keycloak Admin
    API.

    The authentication is handled by the a subclass of :class:`requests.auth.AuthBase`. Use the
    class methods such as :func:`from_client_credentials` or :func:`from_username_password` to
    instantiate a KeycloakAdmin instance with authentication already configured.

    :param server_url: The URL of the Keycloak server (e.g. "https://my-keycloak.com").
    :type server_url: str
    :param realm_name: The name of the realm to interact with for all Admin API calls.
    :type realm_name: str
    :param auth: The authentication instance to use for all requests. See :class:`~.BearerAuth`.
    :type auth: requests.auth.AuthBase
    :param session: The session to use for all request (API and authentication).
        Useful if you need to attach e.g. custom headers to every call.
        Note that `auth` will be overridden, as well as some headers (e.g. `Accept` and `Content-Type`).
    :type session: requests.Session, optional
    """

    def __init__(
        self,
        server_url: str,
        realm_name: str,
        auth: requests.auth.AuthBase,
        session: requests.Session | None = None,
    ):
        super().__init__(
            base_url=f"{server_url}/admin/realms/{realm_name}",
            auth=auth,
            session=session,
            append_slash=False,
        )

    @property
    def session(self) -> requests.Session:
        """
        The session used for all requests.

        :getter: Get the session.
        :type: requests.Session
        """
        return self._store.session

    @property
    def base_url(self) -> str:
        """
        The base URL of the Keycloak Admin REST API (including the realm).

        :getter: Get the base_url.
        :type: string
        """
        return self._store.base_url

    @property
    def realm_name(self) -> str:
        """
        :getter: Get the current realm name.
        :setter: Set the realm name. This updates the :attr:`base_url` and impact all future requests.
        :seealso: :attr:`realms`
        """
        return self._store.base_url.split("/realms/")[1]

    @realm_name.setter
    def realm_name(self, realm_name: str) -> None:
        base_url = self._store.base_url.split("/realms/")[0]
        self._store = evolve(
            self._store, base_url=f"{base_url}/realms/{realm_name}"
        )

    @property
    def realms(self) -> Resource:
        """
        Special resource to interact with the ``/admin/realms/`` endpoint.

        By default, the client base URL contains a realm name, making it impossible to query the
        ``/admin/realms/`` endpoint. This special property allows you to start the URL at ``/realms/``
        instead of ``/realms/{realm_name}``.

        Some example usages:

        .. code-block:: python

            # List all realms
            client.realms.get()
            # Get users in another realm
            client.realms("test").users.get()
            # Get users in the current realm
            client.get() == client.realms(client.realm_name).get()

        """
        base_url = self._store.base_url.split("/realms/")[0]
        return self._get_resource(
            evolve(self._store, base_url=f"{base_url}/realms/")
        )

    @classmethod
    def create(
        cls,
        connection: OpenidConnection,
        realm_name: str | None = None,
    ) -> "KeycloakAdmin":
        """
        Create a KeycloakAdmin from an :class:`~.OpenidConnection`.
        The session from the connection will also be used for all Admin requests.
        You may set a different realm than the one used for authentication
        by setting the `realm_name` parameter.

        :param connection: The connection to use for authentication.
        :type connection: OpenidConnection
        :param realm_name: The name of the realm to interact with for all Admin API calls.
            If not set, the realm name from the `connection` will be used.
        :type realm_name: str, optional
        """
        return cls(
            connection.server_url,
            realm_name or connection.realm_name,
            BearerAuth(connection.token),
            session=connection.session,
        )

    @classmethod
    def from_client_credentials(
        cls,
        server_url: str,
        realm_name: str,
        client_id: str,
        client_secret: str,
        authentication_realm_name: str | None = None,
        session: requests.Session | None = None,
    ) -> "KeycloakAdmin":
        """
        Create a KeycloakAdmin instance using username and password authentication.

        :param server_url: The URL of the Keycloak server (e.g. "https://my-keycloak.com").
        :type server_url: str
        :param realm_name: The name of the realm to interact with for all Admin API calls.
            If you need to authenticate against a different realm, set `authentication_realm_name`.
        :type realm_name: str
        :param client_id: The client ID to authenticate with (e.g. "admin-cli").
        :type client_id: str
        :param username: The username to authenticate with.
        :type username: str
        :param password: The password to authenticate with.
        :type password: str
        :param authentication_realm_name: The realm to authenticate against. If omitted, `realm_name` will be used.
        :type authentication_realm_name: str, optional
        :param session: The session to use for all request (API and authentication).
        :type session: requests.Session, optional
        """
        openid_connection = ClientCredentialsConnection(
            server_url=server_url,
            realm_name=authentication_realm_name or realm_name,
            client_id=client_id,
            client_secret=client_secret,
            session=session,
        )
        return cls.create(
            openid_connection,
            realm_name=realm_name,
        )

    @classmethod
    def from_username_password(
        cls,
        #: The URL of the Keycloak server.
        server_url: str,
        realm_name: str,
        client_id: str,
        username: str,
        password: str,
        authentication_realm_name: str | None = None,
        session: requests.Session | None = None,
    ) -> "KeycloakAdmin":
        """
        Create a KeycloakAdmin instance using username and password authentication.

        :param server_url: The URL of the Keycloak server (e.g. "https://my-keycloak.com").
        :type server_url: str
        :param realm_name: The name of the realm to interact with for all Admin API calls.
            If you need to authenticate against a different realm, set `authentication_realm_name`.
        :type realm_name: str
        :param client_id: The client ID to authenticate with (e.g. "admin-cli").
        :type client_id: str
        :param username: The username to authenticate with.
        :type username: str
        :param password: The password to authenticate with.
        :type password: str
        :param authentication_realm_name: The realm to authenticate against. If omitted, `realm_name` will be used.
        :type authentication_realm_name: str, optional
        :param session: The session to use for all request (API and authentication).
        :type session: requests.Session, optional
        """
        openid_connection = UsernamePasswordConnection(
            server_url=server_url,
            realm_name=authentication_realm_name or realm_name,
            client_id=client_id,
            username=username,
            password=password,
            session=session,
        )

        return cls.create(
            openid_connection,
            realm_name=realm_name,
        )
