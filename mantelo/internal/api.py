"""
This module is highly inspired from the awesome slumber library. I decided to port it to mantelo
(with some improvements) due to the lack of active development in slumber since 2018.

Please, do not use :class:`~.API` directly, but use :class:`~.KeycloakAdmin` instead.
"""

from posixpath import join as pathjoin
from typing import Any, TypeAlias
from urllib.parse import urlsplit, urlunsplit

import requests
import requests.auth
from attrs import evolve, field, frozen

from .. import exceptions
from .serializers import BaseSerializer, JsonSerializer


DecodedResponse: TypeAlias = dict | str | bytes
"""
The decoded response as a dict, or as a string if no serializer is defined
or the body is empty. If the body cannot be decoded, the raw bytes are returned
instead of throwing an error.
"""

HttpResponse: TypeAlias = (
    DecodedResponse | tuple[requests.Response, DecodedResponse]
)
"""
Either the decoded response or a tuple with the raw response and the decoded body
(see :py:meth:`Resource.as_raw`).
"""


def url_join(base: str, *args: Any) -> str:
    """
    Join any number of segments to a base URL.
    Segments not of type string will be converted to strings using :func:`str`.
    """
    scheme, netloc, path, query, fragment = urlsplit(base)
    path = pathjoin(path if len(path) else "/", *(str(x) for x in args))
    return urlunsplit([scheme, netloc, path, query, fragment])


@frozen
class Store:
    """
    The holder of all the state for a given resource.
    It is immutable, use :meth:`evolve` to create a new instance with updated values.
    """

    base_url: str
    """The URL this resource targets."""
    session: requests.Session
    """The session to use for all HTTP requests."""
    serializers: list[BaseSerializer] = field()
    """
    The serializers available for decoding the response's data.
    The first serializer is the default one, used also for encoding the request's data.
    """
    append_slash: bool = True
    """
    Whether to append a slash to the URL before making the request.
    """
    raw: bool = False
    """
    Whether to return the raw response object along with the decoded body.
    """

    @serializers.validator
    def _check_serializers(self, _attribute: str, value: Any) -> None:
        if not isinstance(value, list) or len(value) < 1:
            raise ValueError("At least one serializer is required")

    @property
    def default_serializer(self) -> BaseSerializer:
        """The serializer used to encode the request's data."""
        return self.serializers[0]

    def get_serializer(self, content_type: str) -> BaseSerializer | None:
        """Get the first serializer that matches the given content type, if any."""
        return next(
            (
                s
                for s in self.serializers
                if s.matches_content_type(content_type)
            ),
            None,
        )

    def evolve(self, **kwargs: Any) -> "Store":
        """Create a new instance with the given values mutated."""
        return evolve(self, **kwargs)


class Resource:
    """
    The magic behind URL translation.

    It provides the magic of translating python code to URLs and HTTP calls. Each instance of a
    resource is tied to a specific URL, and can evolve to a new URL by calling an unknown property
    or attribute. To finally make an HTTP call, use one of the defined methods (:meth:`get`,
    :meth:`post`, etc).

    By default, all HTTP calls return the decoded body (see :py:class:`HttpResponse`), but you can
    also get hold of the raw response by calling :func:`as_raw`.

    :param store: The store object that holds all the state for this resource.
    :type store: _Store
    """

    def __init__(self, store: Store):
        self._store = store

    def __getattr__(self, item: str) -> "Resource":
        """
        Add a path segment to the URL.
        """

        # Don't allow access to 'private' by convention attributes.
        # @@@: How would this work with resources names that begin with
        # underscores?
        if item.startswith("_"):
            raise AttributeError(item)

        base_url = url_join(self._store.base_url, item.replace("_", "-"))

        return self._get_resource(self._store.evolve(base_url=base_url))

    def __call__(
        self, id: Any = None, /, url_override: str | None = None
    ) -> "Resource":
        """
        Add a path segment to the URL, or override the URL entirely.

        Use it instead of :func:`__getattr__` either for readability (e.g.
        :python:`api.user("xxx")`), or because the path segment isn't valid Python (e.g.
        :python:`api("123")`).

        :param id: The path segment to add to the URL.
        :type id: any, optional
        :param url_override: The URL to use instead of the current one.
        :type url_override: string, optional
        :return: A new resource with the updated URL.
        :rtype: Resource
        """

        # Short Circuit out if the call is empty
        if id is None and url_override is None:
            return self

        base_url = self._store.base_url

        if id is not None:
            base_url = url_join(self._store.base_url, id)

        if url_override is not None:
            # @@@ This is hacky and we should probably figure out a better way
            #    of handling the case when a POST/PUT doesn't return an object
            #    but a Location to an object that we need to GET.
            base_url = url_override

        return self._get_resource(self._store.evolve(base_url=base_url))

    def _request(
        self,
        method: str,
        data: dict | None = None,
        files: dict | None = None,
        params: dict | None = None,
    ) -> requests.Response:
        serializer = self._store.default_serializer
        url = self.url()

        headers = {"accept": serializer.content_type}
        body: dict | str | None = data

        if not files and data is not None:
            # The files parameter has the priority (and will be used in the body),
            # but if we manually set the content-type, requests will not override it
            # with multipart/form-data.
            headers["content-type"] = serializer.content_type
            body = serializer.dumps(data)

        resp = self._store.session.request(
            method, url, data=body, params=params, files=files, headers=headers
        )

        self._ = resp

        if 400 <= resp.status_code <= 499:
            if resp.status_code == 404:
                raise exceptions.HttpNotFound.from_response(resp)
            raise exceptions.HttpClientError.from_response(resp)

        if 500 <= resp.status_code <= 599:
            raise exceptions.HttpServerError.from_response(resp)

        return resp

    def _parse_response_body(self, resp: requests.Response) -> DecodedResponse:
        if resp.status_code in [204, 205]:
            return ""  # requests.content and requests.text do the same

        try:
            body = resp.text
        except UnicodeDecodeError:
            # In case the encoding is not properly set, return the raw bytes
            return resp.content

        ctype = resp.headers.get("content-type", "").split(";")[0].strip()
        if (
            ctype
            and body
            and (serializer := self._store.get_serializer(ctype))
        ):
            return serializer.loads(body)
        return body

    def _process_response(self, resp: requests.Response) -> HttpResponse:
        if not (200 <= resp.status_code <= 299):
            # TODO: is this check necessary?
            raise ValueError(
                "_process_response only support 2xx status codes, "
                f"got {resp.status_code}"
            )

        decoded = self._parse_response_body(resp)
        if self._store.raw:
            return (resp, decoded)

        return decoded

    def _do_verb_request(
        self,
        verb: str,
        data: dict | None = None,
        files: dict | None = None,
        params: dict | None = None,
    ) -> HttpResponse:
        resp = self._request(verb, data=data, files=files, params=params)
        return self._process_response(resp)

    def as_raw(self) -> "Resource":
        """
        Make the HTTP calls return both the raw response object and the decoded body.
        """
        return self._get_resource(self._store.evolve(raw=True))

    def get(self, **kwargs: Any) -> HttpResponse:
        """
        Do a GET request.

        :param kwargs: The query parameters to send with the request.
        :rtype: HttpResponse
        """
        return self._do_verb_request("GET", params=kwargs)

    def options(self, **kwargs: Any) -> HttpResponse:
        """
        Do an OPTION request.

        :param kwargs: The query parameters to send with the request.
        :rtype: HttpResponse
        """
        return self._do_verb_request("OPTIONS", params=kwargs)

    def head(self, **kwargs: Any) -> HttpResponse:
        """
        Do a HEAD request.

        :param kwargs: The query parameters to send with the request.
        :rtype: HttpResponse
        """
        return self._do_verb_request("HEAD", params=kwargs)

    def post(
        self,
        data: dict | None = None,
        files: dict | None = None,
        **kwargs: Any,
    ) -> HttpResponse:
        """
        Do a POST request.

        :param data: The data to send with the request.
        :type data: dict, optional
        :param files: The files to send with the request. Supersedes :param:data.
            See `requests.post` for more information.
        :type files: dict, optional
        :param kwargs: The query parameters to send with the request.
        :rtype: HttpResponse
        """
        return self._do_verb_request(
            "POST", data=data, files=files, params=kwargs
        )

    def patch(
        self,
        data: dict | None = None,
        files: dict | None = None,
        **kwargs: Any,
    ) -> HttpResponse:
        """
        Do a PATCH request.
        Parameters are the same as :func:`post`.

        :rtype: HttpResponse
        """
        return self._do_verb_request(
            "PATCH", data=data, files=files, params=kwargs
        )

    def put(
        self,
        data: dict | None = None,
        files: dict | None = None,
        **kwargs: Any,
    ) -> HttpResponse:
        """
        Do a PUT request.
        Parameters are the same as :func:`post`.

        :rtype: HttpResponse
        """
        return self._do_verb_request(
            "PUT", data=data, files=files, params=kwargs
        )

    def delete(
        self,
        data: dict | None = None,
        files: dict | None = None,
        **kwargs: Any,
    ) -> bool | tuple[requests.Response, bool]:
        """
        Do a DELETE request.
        Parameters are the same as :func:`post`.

        *Note*: some APIs such as the Keycloak Admin REST Api do not follow the HTTP spec and expect
        a body in the request (e.g.
        ``DELETE /admin/realms/{realm}/users/{user-id}/role-mappings/clients/{client-id}``).


        :return: True if the request was successful, False for 3xx status codes.
        :rtype: bool
        """
        resp = self._request("DELETE", data=data, files=files, params=kwargs)
        # TODO: isn't this stupid?
        # The only other possible statues are 3xx...
        response = 200 <= resp.status_code <= 299

        if self._store.raw:
            return (resp, response)
        return response

    def url(self) -> str:
        """
        Get the URL that will be used for the next HTTP call.
        """
        url = self._store.base_url

        if self._store.append_slash and not url.endswith("/"):
            url = url + "/"

        return url

    def _get_resource(self, *args: Any, **kwargs: Any) -> "Resource":
        return self.__class__(*args, **kwargs)


class API(Resource):
    """
    The main entry point for making HTTP calls to a specific API.

    Highly inspired by the awesome `slumber <https://slumber.readthedocs.io/en/stable/>`_ library,
    this class defines default parameters for all the requests to an API, such as the base URL, the
    serializers to use, and the session to use for all requests. Once you have an API object, you
    can start making calls using, e.g. :python:`api.users.get()`.

    Do NOT use it directly, see :class:`KeycloakAdmin` instead.

    :param base_url: The base URL for the API.
    :type base_url: string
    :param auth: The authentication object to use for all requests.
    :type auth: requests.auth.AuthBase, optional
    :param append_slash: Whether to append a slash to the URL before making the request.
    :type append_slash: bool, optional
    :param session: The session to use for all request (API and authentication).
    :type session: requests.Session, optional
    :param serializers: The serializers to use for encoding and decoding the requests and responses.
        The first serializer in the list is used for encoding the request's data.
        Supports JSON by default.
    :type serializers: list[BaseSerializer], optional
    :param raw: Whether to return the raw response object along with the decoded body.
    :type raw: bool, optional
    """

    _resource_class = Resource

    def __init__(
        self,
        base_url: str,
        auth: requests.auth.AuthBase | None = None,
        append_slash: bool = True,
        session: requests.Session | None = None,
        serializers: list[BaseSerializer] | None = None,
        raw: bool = False,
    ):
        if base_url is None:
            raise ValueError("base_url is required")

        if serializers is None:
            serializers = [JsonSerializer()]

        if session is None:
            session = requests.session()

        if auth is not None:
            session.auth = auth

        self._store = Store(
            base_url=base_url,
            append_slash=append_slash,
            session=session,
            serializers=serializers,
            raw=raw,
        )

    def _get_resource(self, *args: Any, **kwargs: Any) -> "Resource":
        return self._resource_class(*args, **kwargs)
