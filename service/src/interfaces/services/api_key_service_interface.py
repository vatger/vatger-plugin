from abc import ABC, abstractmethod

from domain.api_key import APIKey


class APIKeyServiceInterface(ABC):
    """validates API keys"""

    @abstractmethod
    def validate_key(self, raw_key: str) -> APIKey | None: ...
