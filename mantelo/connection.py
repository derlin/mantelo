from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from logging import getLogger

import requests
from attrs import Factory, define, field, frozen

from .exceptions import AuthenticationException


logger = getLogger(__name__)

_NO_AUTH = lambda r: r  # noqa: E731


# TODO: those converters are ugly, but due to a bug in mypy
# (see https://github.com/python/mypy/issues/6535),
# it is not possible to use the `default_if_none` converter
# for now.
# Proper field arguments to use once fixed:
#   converter=default_if_none(timedelta(seconds=30)),
#   converter=default_if_none(Factory(requests.Session)),
#
def _session_if_none_converter(value) -> requests.Session:
    if value is None:
        return requests.Session()
    assert isinstance(value, requests.Session)
    return value


def _timedelta_if_none_converter(value: timedelta | None) -> timedelta:
    if value is None:
        return timedelta(seconds=30)
    return value


def utcnow():
    return datetime.now(timezone.utc)


class Connection(ABC):
    @abstractmethod
    def token(self) -> str:
        pass  # NOCOV


@frozen
class Token:
    access_token: str
    expires_in: int
    scope: str | None = None
    token_type: str | None = None
    refresh_expires_in: int | None = None
    refresh_token: str | None = None
    created_at: datetime = field(default=Factory(utcnow))

    def __attrs_post_init__(self):
        if self.refresh_token and not self.refresh_expires_in:
            raise TypeError("Missing refresh_expires_in.")

    @property
    def expires_at(self) -> datetime:
        return self.created_at + timedelta(seconds=self.expires_in)

    @property
    def refresh_expires_at(self) -> datetime | None:
        if not self.refresh_token:
            return None
        assert self.refresh_expires_in
        return self.created_at + timedelta(seconds=self.refresh_expires_in)

    def has_refresh_token(self, _now: Callable[[], datetime] = utcnow) -> bool:
        if (exp := self.refresh_expires_at) and _now() < (
            exp - timedelta(seconds=2)
        ):
            return True
        return False

    @classmethod
    def from_dict(cls, data: dict, now: datetime | None = None) -> "Token":
        assert hasattr(cls, "__slots__")
        if now:
            data["created_at"] = now
        return cls(**{k: v for k, v in data.items() if k in cls.__slots__})


@define
class OpenidConnection(Connection, ABC):
    server_url: str
    realm_name: str
    client_id: str

    session: requests.Session = field(
        default=Factory(requests.Session),
        converter=_session_if_none_converter,
        kw_only=True,
    )
    refresh_timeout: timedelta = field(
        default=timedelta(seconds=30),
        converter=_timedelta_if_none_converter,
        kw_only=True,
    )

    _token: Token | None = field(
        init=False, repr=False, eq=False, default=None
    )

    @property
    def auth_url(self) -> str:
        return f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/token"

    @abstractmethod
    def _token_exchange_data(self) -> dict:
        pass  # NOCOV

    def _fetch_token(self) -> None:
        now = utcnow()

        if self._token and self._token.has_refresh_token():
            logger.debug("Refreshing token")
            data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": self._token.refresh_token,
            }
        else:
            logger.debug("Fetching token")
            data = self._token_exchange_data()

        # Ensure the call does not use authentication,
        # to avoid recursion errors.
        resp = self.session.post(self.auth_url, data=data, auth=_NO_AUTH)
        if resp.status_code == 401:
            raise AuthenticationException(**resp.json())
        resp.raise_for_status()
        self._token = Token.from_dict(resp.json(), now=now)
        logger.debug(
            "Token valid for %s, refresh token valid for %s",
            self._token.expires_in,
            self._token.refresh_expires_in,
        )

    def token(self, _now: Callable[[], datetime] = utcnow) -> str:
        if not self._token or _now() > (
            self._token.expires_at - self.refresh_timeout
        ):
            self._fetch_token()

        assert self._token
        return self._token.access_token


@define
class UsernamePasswordConnection(OpenidConnection):
    username: str
    password: str

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
    client_secret: str

    def _token_exchange_data(self) -> dict:
        return {
            "scope": "openid",
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
