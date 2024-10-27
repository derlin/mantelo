import requests
from attrs import field, frozen
from slumber.exceptions import SlumberHttpBaseException


@frozen
class AuthenticationException(Exception):
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
class HttpException(Exception):
    """
    Exception raised on HTTP errors when talking to the Keycloak Admin API.
    """

    status_code: int
    """The HTTP status code."""
    json: dict
    """The JSON response from the server."""
    url: str
    """The URL that was requested."""
    response: requests.Response = field(repr=False)
    """The response object from the server."""

    @classmethod
    def from_slumber_exception(cls, ex: SlumberHttpBaseException):
        assert hasattr(ex, "response")
        return cls(
            url=ex.response.request.url,
            status_code=ex.response.status_code,
            json=ex.response.json() if ex.response.content else {},
            response=ex.response,
        )
