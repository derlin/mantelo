from unittest.mock import MagicMock

import pytest

from mantelo.internal import serializers
from mantelo.connection import (
    ClientCredentialsConnection,
    UsernamePasswordConnection,
)
from mantelo.internal import api

from . import constants


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
    return ClientCredentialsConnection(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.TEST_REALM,
        client_id=constants.TEST_CLIENT_ID,
        client_secret=constants.TEST_CLIENT_SECRET,
    )


@pytest.fixture()
def openid_connection_admin():
    return UsernamePasswordConnection(
        server_url=constants.TEST_SERVER_URL,
        realm_name=constants.MASTER_REALM,
        client_id=constants.ADMIN_CLI_CLIENT,
        username=constants.TEST_MASTER_USER,
        password=constants.TEST_MASTER_PASSWORD,
    )


@pytest.fixture()
def mock_session():
    session = MagicMock()
    session.request.return_value = MagicMock(status_code=200)
    for session_method in ["get", "post", "put", "delete"]:
        getattr(
            session, session_method
        ).return_value = session.request.return_value
    return session


@pytest.fixture()
def mock_store(mock_session):
    return api.Store(
        base_url="https://example.com",
        serializers=[serializers.JsonSerializer()],
        session=mock_session,
        append_slash=False,
        raw=False,
    )
