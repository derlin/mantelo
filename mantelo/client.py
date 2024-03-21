from collections.abc import Callable

import requests
import slumber
from attrs import define
from slumber.exceptions import SlumberHttpBaseException

from .connection import (
    ClientCredentialsConnection,
    OpenidConnection,
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


@define
class BearerAuth(requests.auth.AuthBase):
    token_getter: Callable[[], str]

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token_getter()}"
        return r


class KeycloakAdmin(HypenatedResourceMixin, slumber.API):
    resource_class = HypenatedResource

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
    def session(self):
        return self._store["session"]

    @property
    def base_url(self):
        return self._store["base_url"]

    @property
    def realm_name(self):
        return self._store["base_url"].split("/realms/")[1]

    @realm_name.setter
    def realm_name(self, realm_name):
        base_url = self._store["base_url"].split("/realms/")[0]
        self._store["base_url"] = f"{base_url}/realms/{realm_name}"

    @classmethod
    def create(
        cls,
        connection: OpenidConnection,
        realm_name: str | None = None,
    ):
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
    ):
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
        server_url: str,
        realm_name: str,
        client_id: str,
        username: str,
        password: str,
        authentication_realm_name: str | None = None,
        session: requests.Session | None = None,
    ):
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
