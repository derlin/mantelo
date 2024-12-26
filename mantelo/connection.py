from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from logging import getLogger
from typing import Any

import requests
from attrs import Factory, define, field, frozen

from .exceptions import AuthenticationException


_logger = getLogger(__name__)

_NO_AUTH = lambda r: r  # noqa: E731


# TODO: those converters are ugly, but due to a bug in mypy
# (see https://github.com/python/mypy/issues/6535),
# it is not possible to use the `default_if_none` converter
# for now.
# Proper field arguments to use once fixed:
#   converter=default_if_none(timedelta(seconds=30)),
#   converter=default_if_none(Factory(requests.Session)),
#
def _session_if_none_converter(value: Any) -> requests.Session:
    if value is None:
        return requests.Session()
    assert isinstance(value, requests.Session)
    return value


def _timedelta_if_none_converter(value: timedelta | None) -> timedelta:
    if value is None:
        return timedelta(seconds=30)
    return value


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Connection(ABC):
    """
    A base class for all connections.

    A connection only requires a method to generate a token.
    This is the base class used for all connections.
    """

    @abstractmethod
    def token(self) -> str:
        """
        Return a token usable in a Bearer authentication header.
        See also :class:`~.BearerAuth`.

        :return: A valid token.
        :raises AuthenticationException: If Keycloak returns a 401 when getting a token.
        :raises requests.RequestException: If the request to Keycloak fails with other non-2XX status codes.
        """
        # NOCOV


@frozen
class Token:
    """
    A wrapper around a Keycloak token response.

    This class holds a token and its metadata, as returned by Keycloak.
    A token should at least have an `access_token` and an `expires_in` field.
    Optionally, a `refresh_token` and `refresh_expires_in` can be provided.
    """

    access_token: str
    """The token to use for authentication."""
    expires_in: int
    """The number of seconds (from `created_at`) the token is valid."""
    scope: str | None = None
    """The scope of the token (e.g. "openid")."""
    token_type: str | None = None
    """The type of the token (e.g. "Bearer")."""
    refresh_token: str | None = None
    """The token to use to refresh the access token."""
    refresh_expires_in: int | None = None
    """The number of seconds (from `created_at`) the refresh token is valid."""
    created_at: datetime = field(default=Factory(_utcnow))
    """The time at which the token was created."""

    def __attrs_post_init__(self) -> None:
        if self.refresh_token and not self.refresh_expires_in:
            raise TypeError("Missing refresh_expires_in.")

    @property
    def expires_at(self) -> datetime:
        """
        :getter: The time at which the token expires.
        :type: datetime
        """
        return self.created_at + timedelta(seconds=self.expires_in)

    @property
    def refresh_expires_at(self) -> datetime | None:
        """
        :getter: The time at which the refresh token expires, or None if no refresh token is set.
        """
        if not self.refresh_token:
            return None
        assert self.refresh_expires_in
        return self.created_at + timedelta(seconds=self.refresh_expires_in)

    def has_refresh_token(
        self, _now: Callable[[], datetime] = _utcnow
    ) -> bool:
        """
        Check if a refresh token exists and is still valid.

        :return: True if a refresh token exists and is still valid.
        """
        if (exp := self.refresh_expires_at) and _now() < (
            exp - timedelta(seconds=2)
        ):
            return True
        return False

    @classmethod
    def from_dict(cls, data: dict, now: datetime | None = None) -> "Token":
        """
        Instantiate a :class:`~.Token` from a dictionary, as returned by Keycloak.
        """
        assert hasattr(cls, "__slots__")
        if now:
            data["created_at"] = now
        return cls(**{k: v for k, v in data.items() if k in cls.__slots__})


@define
class OpenidConnection(Connection, ABC):
    """
    A base class for OpenID connections.

    This class handles the fetching and refreshing of a token using the well-known
    OpenId token endpoint. The payload data to send when fetching a token must
    be defined in the subclasses (`_token_exchange_data` method).

    :param server_url: The URL of the Keycloak server (e.g. "https://my-keycloak.com").
    :type server_url: str
    :param realm_name: The name of the realm used for authentication.
    :type realm_name: str
    :param client_id: The client ID used for authentication (e.g. "admin-cli").
    :type client_id: str
    :param session: An optional session to use for authentication requests.
    :type session: requests.Session, optional
    :param refresh_timeout: The amount of seconds a token is guaranteed to be valid.
    :type refresh_timeout: timedelta, optional
    """

    server_url: str
    """The URL of the Keycloak server."""
    realm_name: str
    """The name of the realm used for authentication."""
    client_id: str
    """The client name used for authentication (e.g. "admin-cli")."""

    session: requests.Session = field(
        default=Factory(requests.Session),
        converter=_session_if_none_converter,
        kw_only=True,
    )
    """The session to use for authentication requests."""

    refresh_timeout: timedelta = field(
        default=timedelta(seconds=30),
        converter=_timedelta_if_none_converter,
        kw_only=True,
    )
    """
    The amount of seconds a token is guaranteed to be valid.
    If the existing token expires in less than this amount of time,
    it will be refreshed (or a new token will be fetched).
    """

    _token: Token | None = field(
        init=False, repr=False, eq=False, default=None
    )

    @property
    def auth_url(self) -> str:
        """
        :getter: The URL to use for authentication requests
            (e.g. ""https://my-keycloak.com/realms/my-realm/protocol/openid-connect/token").
        """
        return f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/token"

    @abstractmethod
    def _token_exchange_data(self) -> dict:
        pass  # NOCOV

    def _fetch_token(self) -> None:
        now = _utcnow()

        if self._token and self._token.has_refresh_token():
            _logger.debug("Refreshing token")
            data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": self._token.refresh_token,
            }
        else:
            _logger.debug("Fetching token")
            data = self._token_exchange_data()

        # Ensure the call does not use authentication,
        # to avoid recursion errors.
        resp = self.session.post(self.auth_url, data=data, auth=_NO_AUTH)
        if resp.status_code == 401:
            raise AuthenticationException(**resp.json(), response=resp)
        resp.raise_for_status()
        self._token = Token.from_dict(resp.json(), now=now)
        _logger.debug(
            "Token valid for %s, refresh token valid for %s",
            self._token.expires_in,
            self._token.refresh_expires_in,
        )

    def token(self, _now: Callable[[], datetime] = _utcnow) -> str:
        """
        Get a valid token guaranteed to be valid for at least `refresh_timeout` seconds.
        If no valid token exists, it first tries to use the refresh token,
        and falls back to fetching a new token.

        :return: A valid access token.
        """
        if not self._token or _now() > (
            self._token.expires_at - self.refresh_timeout
        ):
            self._fetch_token()

        assert self._token
        return self._token.access_token


@define
class UsernamePasswordConnection(OpenidConnection):
    """
    An :class:`~OpenidConnection` using username and password for authentication.
    It requests a token using the "password" grant type.
    The user should have the permissions necessary to access the Admin REST API
    endpoints.

    :param server_url: The URL of the Keycloak server (e.g. "https://my-keycloak.com").
    :type server_url: str
    :param realm_name: The name of the realm used for authentication.
    :type realm_name: str
    :param client_id: The client ID used for authentication (e.g. "admin-cli").
    :type client_id: str
    :param username: The username to use for authentication.
    :type username: str
    :param password: The password to use for authentication.
    :type password: str
    :param session: An optional session to use for authentication requests.
    :type session: requests.Session, optional
    :param refresh_timeout: The amount of seconds a token is guaranteed to be valid.
    :type refresh_timeout: timedelta, optional
    """

    username: str
    """The username to use for authentication."""
    password: str
    """The password to use for authentication."""

    def _token_exchange_data(self) -> dict:
        return {
            "scope": "openid",
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
        }


@define
class ClientCredentialsConnection(OpenidConnection):
    """
    An :class:`~OpenidConnection` using client credentials for authentication.
    It requests a token using the "client_credentials" grant type.

    To access the Admin REST API, the client should:
    - have "Client authentication" enabled,
    - support the `Service accounts roles` authentication flow,
    - have one or more service account roles granting access to Admin endpoints.

    :param server_url: The URL of the Keycloak server (e.g. "https://my-keycloak.com").
    :type server_url: str
    :param realm_name: The name of the realm used for authentication.
    :type realm_name: str
    :param client_id: The client ID used for authentication (e.g. "admin-cli").
    :type client_id: str
    :param client_secret: The client secret to use for authentication.
    :type client_secret: str
    :param session: An optional session to use for authentication requests.
    :type session: requests.Session, optional
    :param refresh_timeout: The amount of seconds a token is guaranteed to be valid.
    :type refresh_timeout: timedelta, optional
    """

    client_secret: str
    """The client secret to use for authentication."""

    def _token_exchange_data(self) -> dict:
        return {
            "scope": "openid",
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
