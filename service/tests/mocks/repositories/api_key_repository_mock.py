from interfaces.repositories.api_key_repository_interface import APIKeyRepositoryInterface
from models.api_key import APIKey


class APIKeyRepositoryMock(APIKeyRepositoryInterface):
    def __init__(self, initial: list[APIKey] | None = None):
        self._store: dict[str, APIKey] = {}
        self.calls: int = 0
        self.last_hash: str | None = None

        if initial:
            for key in initial:
                self.add(key)

    def add(self, key: APIKey) -> None:
        self._store[key.key_hash] = key

    def remove(self, key_hash: str) -> None:
        self._store.pop(key_hash, None)

    def clear(self) -> None:
        self._store.clear()

    def get_by_hash(self, hash_value: str) -> APIKey | None:
        self.calls += 1
        self.last_hash = hash_value
        return self._store.get(hash_value)
