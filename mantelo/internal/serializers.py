import json
from abc import ABC, abstractmethod


class BaseSerializer(ABC):
    """Abstract base class for all serializers."""

    @property
    def content_type(self) -> str | None:
        """Default content-type for this serializer."""
        return next(iter(self.supported_content_types), None)

    @property
    @abstractmethod
    def supported_content_types(self) -> list[str]:
        """
        Get all the content types this serializer can handle.

        :return: A list of supported content types.
        :rtype: list
        """

    def matches_content_type(self, content_type: str) -> bool:
        """
        Check if the given content type is supported by this serializer.

        :param content_type: The content type to match.
        :return: True if the content type is supported, False otherwise.
        """
        return content_type in self.supported_content_types

    @abstractmethod
    def loads(self, data: str) -> dict:
        """
        Deserialize a string into a dictionary.

        :param data: The string to deserialize.
        :return: The deserialized dictionary.
        :rtype: dict
        """

    @abstractmethod
    def dumps(self, data: dict) -> str:
        """
        Serialize a dictionary into a string.

        :param data: The dictionary to serialize.
        :return: The serialized string.
        :rtype: str
        """


class JsonSerializer(BaseSerializer):
    """A serializer for JSON data."""

    @property
    def supported_content_types(self) -> list[str]:
        return [
            "application/json",
            "application/x-javascript",
            "text/javascript",
            "text/x-javascript",
            "text/x-json",
        ]

    def loads(self, data: str) -> dict:
        return json.loads(data)

    def dumps(self, data: dict) -> str:
        return json.dumps(data)
