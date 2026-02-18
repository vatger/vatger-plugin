from interfaces.repositories.api_key_repository_interface import APIKeyRepositoryInterface
from interfaces.services.api_key_service_interface import APIKeyServiceInterface
from models.api_key import APIKey


class APIKeyService(APIKeyServiceInterface):
    def __init__(self, repository: APIKeyRepositoryInterface, hasher=hash):
        self.repo = repository
        self._hasher = hasher

    def validate_key(self, raw_key: str) -> APIKey | None:
        key_hash = self._hasher(raw_key)
        key = self.repo.get_by_hash(key_hash)

        if not key:
            return None

        if not key.active:
            return None

        return key
