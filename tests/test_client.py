import pytest
import requests

from mantelo import KeycloakAdmin
from mantelo.client import BearerAuth
from mantelo.exceptions import HttpException

from . import constants


@pytest.mark.integration
def test_init(openid_connection_password):
    session = requests.Session()
    adm = KeycloakAdmin(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        auth=BearerAuth(openid_connection_password.token),
        session=session,
    )

    assert adm.session == session
    assert adm.realm_name == constants.TEST_REALM
    assert (
        adm.base_url
        == f"{constants.TEST_SERVER_URL}/admin/realms/{constants.TEST_REALM}"
    )

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.integration
def test_create(openid_connection_sa):
    adm = KeycloakAdmin.create(openid_connection_sa)

    assert adm.session == openid_connection_sa.session
    assert adm.realm_name == openid_connection_sa.realm_name
    assert (
        adm.base_url
        == f"{openid_connection_sa.server_url}/admin/realms/{openid_connection_sa.realm_name}"
    )
    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.integration
@pytest.mark.parametrize("with_custom_session", [True, False])
def test_password_connection(with_custom_session):
    session = requests.Session() if with_custom_session else None

    adm = KeycloakAdmin.from_username_password(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        client_id=constants.ADMIN_CLI_CLIENT,
        username=constants.TEST_USER,
        password=constants.TEST_PASSWORD,
        session=session,
    )

    assert adm.session == adm.session.auth.token_getter.__self__.session
    if session:
        assert adm.session == session

    resp = adm.get()
    assert resp.get("realm") == constants.TEST_REALM


@pytest.mark.integration
def test_client_connection():
    adm = KeycloakAdmin.from_client_credentials(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        client_id=constants.TEST_CLIENT_ID,
        client_secret=constants.TEST_CLIENT_SECRET,
    )

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.integration
def test_different_auth_realm(openid_connection_admin):
    adm = KeycloakAdmin.from_username_password(
        server_url=openid_connection_admin.server_url,
        realm_name=constants.TEST_REALM,
        client_id=openid_connection_admin.client_id,
        username=openid_connection_admin.username,
        password=openid_connection_admin.password,
        authentication_realm_name=openid_connection_admin.realm_name,
    )

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.integration
def test_switch_realm(openid_connection_admin):
    adm = KeycloakAdmin.create(connection=openid_connection_admin)
    assert openid_connection_admin.realm_name == constants.MASTER_REALM
    assert adm.realm_name == constants.MASTER_REALM

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_MASTER_USER in resp

    # Switch to another realm
    adm.realm_name = constants.TEST_REALM

    assert adm.realm_name == constants.TEST_REALM
    assert openid_connection_admin.realm_name == constants.MASTER_REALM

    resp = [u["username"] for u in adm.users.get()]
    assert constants.TEST_USER in resp


@pytest.mark.parametrize(
    ("status", "op"),
    [
        (403, lambda c: c.clients.get()),
        (400, lambda c: c.users.post({"foo": "bar"})),
        (400, lambda c: c.users.post({})),
        (405, lambda c: c.groups.head()),
        (405, lambda c: c.users.put({})),
        (404, lambda c: c.users("not-exist").get()),
        (
            401,
            lambda c: (
                setattr(c._store.session, "auth", None),
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
    assert isinstance(ex.json, dict)
    assert isinstance(ex.response, requests.Response)


@pytest.mark.integration
def test_headers(openid_connection_password):
    headers = {"foo": "foo", "bar": "bar"}

    adm = KeycloakAdmin.create(
        connection=openid_connection_password,
    )
    adm.session.headers.update(headers)

    # Trigger an exception to get the request object
    with pytest.raises(HttpException) as excinfo:
        adm.non_existant.get()

    hs = excinfo.value.response.request.headers
    for k, v in headers.items():
        assert hs.get(k) == v


def test_resource_private(openid_connection_password):
    adm = KeycloakAdmin.create(connection=openid_connection_password)

    with pytest.raises(AttributeError, match="_users"):
        adm._users.get()


def test_client_as_resource():
    adm = KeycloakAdmin(server_url="any", realm_name="any", auth=object)

    # Ensure the client itself defines the get, etc operations
    # (to query /admin/realms/{realm_name}/)
    for op in ["head", "get", "post", "put", "delete"]:
        assert hasattr(adm.clients, op)
        assert f"bound method Resource.{op}" in str(getattr(adm, op))


@pytest.mark.integration
def test_realms_endpoint(openid_connection_admin):
    adm = KeycloakAdmin.create(connection=openid_connection_admin)

    assert len(adm.realms.get()) == 2
    assert adm.get() == adm.realms(constants.MASTER_REALM).get()
