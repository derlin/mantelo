import pytest

from attrs import evolve
from mantelo.connection import (
    Token,
    AuthenticationException,
    ClientCredentialsConnection,
    UsernamePasswordConnection,
)
from datetime import datetime, timedelta, timezone
import requests


def test_token_from_dict():
    now = datetime.now(timezone.utc)
    one_sec = timedelta(seconds=1)

    token = Token.from_dict(
        data={
            "access_token": "tok",
            "expires_in": 3600,
            "refresh_token": "rtok",
            "refresh_expires_in": 6000,
            "scope": "openid",
            # ignored
            "foo": "bar",
        }
    )

    assert token.access_token == "tok"
    assert token.refresh_token == "rtok"
    assert token.scope == "openid"
    assert token.token_type is None
    assert now - one_sec < token.created_at < now + one_sec


def test_refresh_without_expire():
    with pytest.raises(TypeError, match="Missing refresh_expires_in."):
        Token(
            access_token="<any>",
            expires_in=123,
            refresh_token="<set>",
        )


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"access_token": "set"},
        {"access_token": "set", "refresh_token": "set"},
    ],
)
def test_token_from_dict_fails(data):
    with pytest.raises(TypeError):
        Token.from_dict(data=data)


def test_expires_at():
    now = datetime.now(timezone.utc)
    token = Token(
        access_token="<any>",
        expires_in=3600,
        refresh_token="<any>",
        refresh_expires_in=3600,
        created_at=now - timedelta(seconds=3600),
    )

    assert token.expires_at == now
    assert token.refresh_expires_at == now

    token = evolve(token, refresh_token=None)
    assert token.refresh_expires_at is None


@pytest.mark.parametrize(
    ("ok", "token", "now_delta"),
    [
        (False, None, 0),
        (False, "<rt>", 3600),
        (False, "<rt>", 3598),
        (True, "<rt>", 3597),
        (True, "<rt>", 0),
    ],
)
def test_token_has_refresh_token(ok, token, now_delta):
    now = datetime.now(timezone.utc)

    token = Token(
        access_token="<any>",
        expires_in=3600,
        refresh_token=token,
        refresh_expires_in=3600,
        created_at=now,
    )
    res = token.has_refresh_token(
        _now=lambda: now + timedelta(seconds=now_delta)
    )

    assert res == ok


def test_userpasswordconnection_init():
    conn = UsernamePasswordConnection(
        server_url="https://kc.test",
        realm_name="test",
        client_id="foo-client",
        username="u",
        password="p",
    )
    assert (
        conn.auth_url
        == "https://kc.test/realms/test/protocol/openid-connect/token"
    )
    assert conn._token_exchange_data() == {
        "scope": "openid",
        "grant_type": "password",
        "client_id": "foo-client",
        "username": "u",
        "password": "p",
    }
    assert isinstance(conn.session, requests.Session)
    assert conn.refresh_timeout == timedelta(seconds=30)


def test_ClientCredentialsconnection_init():
    conn = ClientCredentialsConnection(
        server_url="https://kc.test",
        realm_name="test",
        client_id="foo-client",
        client_secret="s3cr3t",
    )
    assert (
        conn.auth_url
        == "https://kc.test/realms/test/protocol/openid-connect/token"
    )
    assert conn._token_exchange_data() == {
        "scope": "openid",
        "grant_type": "client_credentials",
        "client_id": "foo-client",
        "client_secret": "s3cr3t",
    }
    assert isinstance(conn.session, requests.Session)
    assert conn.refresh_timeout == timedelta(seconds=30)


def test_openidconnection_default_values():
    args = dict(
        server_url="https://kc.test",
        realm_name="test",
        client_id="foo-client",
        client_secret="s3cr3t",
    )

    # Defaults
    conn = ClientCredentialsConnection(**args)
    assert isinstance(conn.session, requests.Session)
    assert conn.refresh_timeout == timedelta(seconds=30)

    # Override defaults
    session = requests.Session()
    timeout = timedelta(seconds=120)
    conn = ClientCredentialsConnection(
        **args,
        session=session,
        refresh_timeout=timeout,
    )
    assert conn.session == session
    assert conn.refresh_timeout == timeout

    # None values fallback to the default values
    conn = ClientCredentialsConnection(
        **args,
        session=None,
        refresh_timeout=None,
    )
    assert isinstance(conn.session, requests.Session)
    assert conn.refresh_timeout == timedelta(seconds=30)


@pytest.mark.integration
def test_openid_token(openid_connection_password):
    assert not openid_connection_password._token

    # first fetch
    access_token = openid_connection_password.token()
    assert access_token

    # second fetch: same
    assert openid_connection_password.token() == access_token

    # token expired: use refresh token
    openid_connection_password._token = evolve(
        openid_connection_password._token,
        created_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    assert openid_connection_password.token() != access_token

    # token expired and no refresh still works
    access_token = openid_connection_password.token()
    openid_connection_password._token = evolve(
        openid_connection_password._token,
        refresh_token=None,
        created_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    assert openid_connection_password.token() != access_token
    assert openid_connection_password._token.expires_at > datetime.now(
        timezone.utc
    )


@pytest.mark.integration
def test_openid_refresh_token(openid_connection_password):
    assert not openid_connection_password._token

    openid_connection_password._fetch_token()
    token = openid_connection_password._token
    assert token
    assert token.has_refresh_token()

    openid_connection_password.password = "invalid"
    openid_connection_password._fetch_token()
    assert openid_connection_password._token
    assert openid_connection_password._token.expires_at > token.expires_at


@pytest.mark.integration
def test_openid_token_fails(openid_connection_password):
    assert not openid_connection_password._token

    openid_connection_password.password = "wrong"
    with pytest.raises(AuthenticationException) as excinfo:
        openid_connection_password.token()

    assert excinfo.value.error == "invalid_grant"
    assert excinfo.value.error_description == "Invalid user credentials"
    assert isinstance(excinfo.value.response, requests.Response)

    openid_connection_password.username = None
    with pytest.raises(AuthenticationException) as excinfo:
        openid_connection_password.token()

    assert excinfo.value.error == "invalid_request"
    assert excinfo.value.error_description == "Missing parameter: username"
    assert isinstance(excinfo.value.response, requests.Response)
