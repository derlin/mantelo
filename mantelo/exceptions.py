import requests
from attrs import field, frozen


@frozen
class ManteloException(Exception):
    """
    Base exception for all exceptions raised by the Mantelo library.
    """


@frozen
class AuthenticationException(ManteloException):
    """
    Exception raised when the authentication request fails with a `401 Unauthorized` status code.
    """

    error: str
    """The error message from Keycloak."""
    error_description: str
    """The error description from Keycloak."""
    response: requests.Response = field(repr=False)
    """The response object from the server."""


@frozen
class HttpException(ManteloException):
    """
    Exception raised on HTTP errors when talking to the Keycloak Admin API.
    """

    status_code: int
    """The HTTP status code."""
    json: dict
    """The JSON response from the server, or an empty JSON if the body is not JSON."""
    url: str
    """The URL that was requested."""
    response: requests.Response = field(repr=False)
    """The response object from the server."""

    @classmethod
    def from_response(cls, response: requests.Response) -> "HttpException":
        json = {}
        try:
            # Most API use JSON, but not all!
            json = response.json()
        except Exception:  # noqa: S110
            pass

        return cls(
            url=response.request.url or "",
            status_code=response.status_code,
            json=json,
            response=response,
        )


@frozen
class HttpClientError(HttpException):
    """
    Called when the server tells us there was a client error (4xx).
    """


class HttpNotFound(HttpClientError):
    """
    Called when the server sends a 404 error.
    """


class HttpServerError(HttpException):
    """
    Called when the server tells us there was a server error (5xx).
    """


class SerializerNoAvailable(ManteloException):
    """
    The serializer for the content type is not available.
    """
