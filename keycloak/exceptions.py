import requests
from attrs import field, frozen
from slumber.exceptions import SlumberHttpBaseException


@frozen
class AuthenticationException(Exception):
    error: str
    error_description: str


@frozen
class HttpException(Exception):
    status_code: int
    json: str
    url: str
    response: requests.Response = field(repr=False)

    @classmethod
    def from_slumber_exception(cls, ex: SlumberHttpBaseException):
        assert hasattr(ex, "response")
        return cls(
            url=ex.response.request.url,
            status_code=ex.response.status_code,
            json=ex.response.json(),
            response=ex.response,
        )
