from unittest.mock import MagicMock, Mock, PropertyMock

import pytest
import requests

from mantelo.internal import api as _api
from mantelo import exceptions
from mantelo.internal.serializers import JsonSerializer


def test_store_evolve(mock_store):
    new_store = mock_store.evolve(
        base_url="new_base_url",
        raw=True,
    )

    assert isinstance(new_store, _api.Store)
    assert new_store != mock_store
    assert new_store.session == mock_store.session
    assert new_store.base_url == "new_base_url"
    assert new_store.raw is True


@pytest.mark.parametrize("serializers", [[], None, "not a list"])
def test_store_validate_serializers(mock_store, serializers):
    with pytest.raises(ValueError) as excinfo:
        mock_store.evolve(serializers=serializers)
    assert str(excinfo.value) == "At least one serializer is required"


@pytest.mark.parametrize(
    ("base", "parts", "expected"),
    [
        ("", [], "/"),
        ("/", [], "/"),
        ("/some/path/", ["test", "foo"], "/some/path/test/foo"),
        ("http://example.com", [], "http://example.com/"),
        ("https://port.com:433/foo", [], "https://port.com:433/foo"),
        (
            "http://path-in-base.com/path/test/",
            ["foo/"],
            "http://path-in-base.com/path/test/foo/",
        ),
        (
            "http://slashes.com/",
            ["/test/", "foo"],
            "http://slashes.com/test/foo",
        ),
        (
            "http://to-string.com",
            ["test", 1, "bar", False],
            "http://to-string.com/test/1/bar/False",
        ),
    ],
)
def test_url_join(base, parts, expected):
    assert _api.url_join(base, *parts) == expected


@pytest.mark.parametrize(
    "base_url", ["http://x.com", "http://x.com/something"]
)
@pytest.mark.parametrize(
    ("resource", "expected_path"),
    [
        (lambda api: api, ""),
        (lambda api: api.foo, "foo"),
        (lambda api: api.foo.bar, "foo/bar"),
        (lambda api: api.foo("123").bar, "foo/123/bar"),
        (lambda api: api.foo(123).bar(), "foo/123/bar"),
        (lambda api: api.under_score, "under-score"),
        (lambda api: api("under-score")("foo-bar"), "under-score/foo-bar"),
    ],
)
@pytest.mark.parametrize("append_slash", [True, False])
def test_resource_url(base_url, resource, expected_path, append_slash):
    api = _api.API(base_url=base_url, append_slash=append_slash)

    expected = f"{base_url}/{expected_path}" if expected_path else base_url
    if append_slash:
        expected += "/"

    assert resource(api).url() == expected


def test_resource_url_override():
    api = _api.API(base_url="A")
    # It replaces everything so far
    assert api(url_override="B").url() == "B/"
    assert api.foo.bar(url_override="B").buzz.url() == "B/buzz/"
    assert api.foo.bar(url_override="B").buzz(url_override="C").url() == "C/"


def test_resource_request(mock_store):
    mock_response = mock_store.session.request.return_value
    resource = _api.Resource(
        mock_store.evolve(
            base_url="base_url",
            serializers=[Mock(content_type="ctype")],
        )
    )

    assert (
        resource._request("METHOD", files="file", params="params")
        == mock_response
    )
    assert resource._ == mock_response

    mock_store.session.request.assert_called_with(
        "METHOD",
        "base_url",
        data=None,
        params="params",
        files="file",
        headers={"accept": "ctype"},
    )


@pytest.mark.parametrize("append_slash", [True, False])
def test_resource_request_append_slash(mock_session, mock_store, append_slash):
    resource = _api.Resource(
        mock_store.evolve(
            base_url="https://example.com/foo",
            append_slash=append_slash,
        )
    )
    resource._request("METHOD")
    mock_session.request.assert_called_once()
    if append_slash:
        assert (
            mock_session.request.call_args[0][1] == "https://example.com/foo/"
        )
    else:
        assert (
            mock_session.request.call_args[0][1] == "https://example.com/foo"
        )


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (100, None),
        (200, None),
        (300, None),
        (400, exceptions.HttpClientError),
        (404, exceptions.HttpNotFound),
        (499, exceptions.HttpClientError),
        (500, exceptions.HttpServerError),
        (599, exceptions.HttpServerError),
    ],
)
def test_resource_request_http_response(
    mock_store, mock_session, status_code, expected
):
    mock_response = Mock(status_code=status_code)
    mock_session.request.return_value = mock_response
    resource = _api.Resource(mock_store)

    if expected is None:
        assert resource._request("METHOD") == mock_response
    else:
        with pytest.raises(expected) as excinfo:
            resource._request("METHOD")
        assert excinfo.value.response == mock_response


def test_resource_request_body(mock_store):
    mock_store.session.request.return_value = Mock(status_code=200)
    resource = _api.Resource(mock_store)

    # the data should be serialized and the content-type header set
    resource._request("POST", data={"foo": "bar"})
    mock_store.session.request.assert_called_with(
        "POST",
        "https://example.com",
        data='{"foo": "bar"}',
        params=None,
        files=None,
        headers={
            "accept": "application/json",
            "content-type": "application/json",
        },
    )

    # if files is provided, data should be sent raw and more importantly
    # the content-type should NOT be set
    mock_store.session.reset_mock()
    resource._request("POST", data={"foo": "bar"}, files="file")
    mock_store.session.request.assert_called_with(
        "POST",
        "https://example.com",
        data={"foo": "bar"},  # will be ignored by requests anyway
        params=None,
        files="file",
        headers={"accept": "application/json"},
    )


@pytest.mark.parametrize("status_code", [204, 205])
def test_resource_parse_response_body_skip(status_code):
    resource = _api.Resource(Mock())
    assert resource._parse_response_body(Mock(status_code=status_code)) == ""


@pytest.mark.parametrize(
    ("content_type", "content"),
    [
        (None, None),
        ("application/json", None),
        ("application/json", ""),
        (None, '{"foo": "bar"}'),
        ("", '{"foo": "bar"}'),
    ],
)
def test_resource_parse_response_body_no_decode(content_type, content):
    mock_response = Mock(status_code=200, text=content, headers={})
    if content_type is not None:
        mock_response.headers = {"content-type": content_type}

    resource = _api.Resource(Mock())
    assert resource._parse_response_body(mock_response) == mock_response.text
    resource._store.get_serializer.assert_not_called()


def test_resource_parse_response_bytes():
    mock_response = Mock(
        status_code=200,
        content=b"bytes",
        headers={},
    )
    # Make resp.text raise an exception
    type(mock_response).text = PropertyMock(
        side_effect=UnicodeDecodeError("", b"", 0, 1, "")
    )

    resource = _api.Resource(Mock())
    assert resource._parse_response_body(mock_response) == b"bytes"
    resource._store.get_serializer.assert_not_called()


@pytest.mark.parametrize(
    ("ctype", "expected"),
    [
        ("FOO-BAR", None),
        ("foobar", None),
        ("foo-bar;", 0),
        ("  foo-bar    ;   ", 0),
        ("application/json", 2),
        ("application/json; charset=utf-8", 2),
        ("text/json;", None),
    ],
)
def test_resource_parse_response_body_choose_serializer(ctype, expected):
    mock_response = Mock(
        status_code=200,
        text="any",
        headers={"content-type": ctype},
    )

    resource = _api.Resource(
        _api.Store(
            base_url="any",
            session=Mock(),
            serializers=[
                MagicMock(matches_content_type=lambda s: s == "foo-bar"),
                MagicMock(matches_content_type=lambda s: s == "text/yaml"),
                MagicMock(
                    matches_content_type=lambda s: s == "application/json"
                ),
            ],
        )
    )
    resp = resource._parse_response_body(mock_response)

    if expected is None:
        assert resp == "any"
    else:
        assert resp == resource._store.serializers[expected].loads.return_value


@pytest.mark.parametrize("raw", [True, False])
def test_resource_process_response(mock_store, raw):
    resource = _api.Resource(mock_store.evolve(raw=raw))
    resource._parse_response_body = Mock(return_value="decoded")
    mock_response = Mock(status_code=200)

    result = resource._process_response(mock_response)
    if raw:
        assert result == (mock_response, "decoded")
    else:
        assert result == "decoded"


def test_resource_process_response_invalid_status(mock_store):
    resource = _api.Resource(mock_store.evolve(raw=False))

    with pytest.raises(ValueError) as excinfo:
        resource._process_response(Mock(status_code=500))

    assert (
        str(excinfo.value)
        == "_process_response only support 2xx status codes, got 500"
    )


def test_resource_do_verb_request(mock_store):
    resource = _api.Resource(mock_store)
    resource._request = Mock(return_value="response")
    resource._process_response = Mock()

    resource._do_verb_request(
        "GET", data="data", files="files", params="params"
    )

    resource._request.assert_called_with(
        "GET", data="data", files="files", params="params"
    )
    resource._process_response.assert_called_with("response")


def test_resource_as_raw(mock_store):
    resource = _api.Resource(mock_store.evolve(raw=False))
    response = resource.as_raw()

    assert isinstance(response, _api.Resource)
    assert response != resource
    assert response._store.raw is True


@pytest.mark.parametrize("method", ["get", "options", "head"])
def test_resource_get_options_head(mock_store, method):
    resource = _api.Resource(mock_store)
    resource._do_verb_request = Mock(return_value="response")

    assert getattr(resource, method)(foo="bar") == "response"

    resource._do_verb_request.assert_called_with(
        method.upper(), params={"foo": "bar"}
    )


@pytest.mark.parametrize("method", ["post", "patch", "put"])
def test_resource_post_patch_put(mock_store, method):
    resource = _api.Resource(mock_store)
    resource._do_verb_request = Mock(return_value="response")

    assert (
        getattr(resource, method)(data="data", files="files", foo="bar")
        == "response"
    )

    resource._do_verb_request.assert_called_with(
        method.upper(), data="data", files="files", params={"foo": "bar"}
    )


@pytest.mark.parametrize(
    ("status_code", "expected"), [(200, True), (301, False)]
)
@pytest.mark.parametrize("raw", [True, False])
def test_resource_delete(mock_store, raw, status_code, expected):
    mock_response = Mock(status_code=status_code)
    resource = _api.Resource(mock_store.evolve(raw=raw))
    resource._request = Mock(return_value=mock_response)

    response = resource.delete(data="data", files="files", foo="bar")

    resource._request.assert_called_with(
        "DELETE", data="data", files="files", params={"foo": "bar"}
    )

    if raw:
        assert response == (mock_response, expected)
    else:
        assert response == expected


def test_api_init():
    with pytest.raises(ValueError) as excinfo:
        _api.API(base_url=None)
    assert str(excinfo.value) == "base_url is required"

    # Test default values
    api = _api.API(base_url="http://example.com")
    assert isinstance(api._store.default_serializer, JsonSerializer)
    assert isinstance(api._store.session, requests.Session)
    assert api._store.append_slash is True
    assert api._store.raw is False

    # Test auth
    api = _api.API(base_url="http://example.com", auth="auth")
    assert api._store.session.auth == "auth"

    # Test empty serializers
    with pytest.raises(ValueError):
        _api.API(base_url="http://example.com", serializers=[])
