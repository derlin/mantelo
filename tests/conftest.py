from mantelo.connection import UsernamePasswordConnection, ServiceAccountConnection
from . import constants
import pytest

@pytest.fixture()
def openid_connection_password():
    return UsernamePasswordConnection(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        client_id=constants.ADMIN_CLI_CLIENT,
        username=constants.TEST_USER,
        password=constants.TEST_PASSWORD,
    )


@pytest.fixture()
def openid_connection_sa():
    return ServiceAccountConnection(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        client_id=constants.TEST_CLIENT_ID,
        client_secret=constants.TEST_CLIENT_SECRET,
    )
