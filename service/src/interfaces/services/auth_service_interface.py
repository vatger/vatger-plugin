from abc import ABC, abstractmethod

from domain.api_key import APIKey


class ApiKeyAuthServiceInterface(ABC):
    """checks if the API key has the required permissions"""

    @abstractmethod
    def authorize(self, raw_key: str, required: set[str]) -> APIKey: ...
