from abc import ABC, abstractmethod

from domain.api_key import APIKey


class APIKeyRepositoryInterface(ABC):
    @abstractmethod
    def get_by_hash(self, hash_value: str) -> APIKey: ...
