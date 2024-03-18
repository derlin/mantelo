from collections.abc import Callable

import requests
import slumber
from slumber.exceptions import SlumberHttpBaseException

from .connection import (
    OpenidConnection,
    ServiceAccountConnection,
    UsernamePasswordConnection,
)
from .exceptions import HttpException


class HypenatedResourceMixin(slumber.ResourceAttributesMixin):
    def __getattr__(self, item):
        if item.startswith("_"):
            raise AttributeError(item)
        return super().__getattr__(item.replace("_", "-"))


class HypenatedResource(HypenatedResourceMixin, slumber.Resource):
    def _request(self, *args, **kwargs):
        try:
            return slumber.Resource._request(self, *args, **kwargs)
        except SlumberHttpBaseException as ex:
            raise HttpException.from_slumber_exception(ex) from None


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token_getter: Callable[[], str]):
        self._token_getter = token_getter

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self._token_getter()}"
        return r


class KeycloakAdmin(HypenatedResourceMixin, slumber.API):
    resource_class = HypenatedResource

    def __init__(
        self,
        server_url: str,
        realm_name: str,
        auth: requests.auth.AuthBase,
        session: requests.Session | None = None,
        headers: dict[str, str] | None = None,
    ):
        if headers:
            if not session:
                session = requests.session()
            session.headers.update(headers)

        super().__init__(
            base_url=f"{server_url}/admin/realms/{realm_name}",
            auth=auth,
            session=session,
            append_slash=False,
        )

    @classmethod
    def create(
        cls,
        connection: OpenidConnection,
        realm_name: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        return cls(
            connection.server_url,
            realm_name or connection.realm_name,
            BearerAuth(connection.token),
            headers=headers,
        )

    @classmethod
    def from_service_account(
        cls,
        server_url: str,
        realm_name: str,
        client_id: str,
        client_secret: str,
        authentication_realm_name: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        openid_connection = ServiceAccountConnection(
            server_url=server_url,
            realm_name=authentication_realm_name or realm_name,
            client_id=client_id,
            client_secret=client_secret,
        )
        return cls.create(
            openid_connection,
            realm_name=realm_name,
            headers=headers,
        )

    @classmethod
    def from_credentials(
        cls,
        server_url: str,
        realm_name: str,
        client_id: str,
        username: str,
        password: str,
        authentication_realm_name: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        openid_connection = UsernamePasswordConnection(
            server_url=server_url,
            realm_name=authentication_realm_name or realm_name,
            client_id=client_id,
            username=username,
            password=password,
        )
        return cls.create(
            openid_connection,
            realm_name=realm_name,
            headers=headers,
        )
