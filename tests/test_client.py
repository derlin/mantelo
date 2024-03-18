import pytest
from . import constants
from mantelo import KeycloakAdmin
from mantelo.client import BearerAuth
from mantelo.exceptions import HttpException
import requests


@pytest.mark.integration
def test_init(openid_connection_password):
    session = requests.Session()
    adm = KeycloakAdmin(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        auth=BearerAuth(openid_connection_password.token),
        session=session,
        headers={"foo": "bar"},
    )

    s = adm._store["session"]
    assert s == session
    assert s.headers.get("foo") == "bar"

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.integration
def test_create(openid_connection_sa):
    adm = KeycloakAdmin.create(openid_connection_sa)

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.integration
def test_password_connection():
    adm = KeycloakAdmin.from_credentials(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        client_id=constants.ADMIN_CLI_CLIENT,
        username=constants.TEST_USER,
        password=constants.TEST_PASSWORD,
    )

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.integration
def test_admin_password_connection():
    adm = KeycloakAdmin.from_credentials(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        client_id=constants.ADMIN_CLI_CLIENT,
        username=constants.TEST_MASTER_USER,
        password=constants.TEST_MASTER_PASSWORD,
        authentication_realm_name=constants.MASTER_REALM,
    )

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.integration
def test_client_connection():
    adm = KeycloakAdmin.from_service_account(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        client_id=constants.TEST_CLIENT_ID,
        client_secret=constants.TEST_CLIENT_SECRET,
    )

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.parametrize(
    ("status", "op"),
    [
        (403, lambda c: c.clients.get()),
        (400, lambda c: c.users.post({"foo": "bar"})),
        (400, lambda c: c.users.post({})),
        (405, lambda c: c.users.put({})),
        (404, lambda c: c.users("not-exist").get()),
        (
            401,
            lambda c: (
                setattr(c._store["session"], "auth", None),
                c.users.get(),
            )[-1],
        ),
    ],
)
@pytest.mark.integration
def test_exceptions(openid_connection_password, status, op):
    adm = KeycloakAdmin.create(
        connection=openid_connection_password,
        realm_name=constants.TEST_REALM,
    )

    with pytest.raises(HttpException) as excinfo:
        op(adm)

    ex = excinfo.value
    assert ex.status_code == status
    assert ex.url.startswith(constants.TEST_SERVER_URL)
    assert ex.json and isinstance(ex.json, dict)
    assert isinstance(ex.response, requests.Response)


def test_headers(openid_connection_password):
    headers = {"foo": "foo", "bar": "bar"}
    adm = KeycloakAdmin.create(
        connection=openid_connection_password,
        headers=headers,
    )

    session_headers = adm._store["session"].headers
    for k, v in headers.items():
        assert session_headers.get(k) == v


def test_resource_private(openid_connection_password):
    adm = KeycloakAdmin.create(connection=openid_connection_password)

    with pytest.raises(AttributeError, match="_users"):
        adm._users.get()
