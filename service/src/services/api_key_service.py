import hashlib
from collections.abc import Callable

from domain.api_key import APIKey
from interfaces.repositories.api_key_repository_interface import APIKeyRepositoryInterface
from interfaces.services.api_key_service_interface import APIKeyServiceInterface


def sha256_hex(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class APIKeyService(APIKeyServiceInterface):
    def __init__(
        self, repository: APIKeyRepositoryInterface, hasher: Callable[[str], str] = sha256_hex
    ):
        self.repo = repository
        self._hasher = hasher

    def validate_key(self, raw_key: str) -> APIKey | None:
        key_hash = self._hasher(raw_key)
        key = self.repo.get_by_hash(key_hash)

        if not key or not key.active:
            return None

        return key
