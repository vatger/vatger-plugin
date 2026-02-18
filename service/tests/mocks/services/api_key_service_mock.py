from interfaces.services.api_key_service_interface import APIKeyServiceInterface
from models.api_key import APIKey


class APIKeyServiceMock(APIKeyServiceInterface):
    def __init__(self, initial: dict[str, APIKey] | None = None):
        self._store: dict[str, APIKey] = dict(initial or {})
        self.calls: int = 0
        self.last_raw_key: str | None = None

    def set(self, raw_key: str, api_key: APIKey) -> None:
        self._store[raw_key] = api_key

    def remove(self, raw_key: str) -> None:
        self._store.pop(raw_key, None)

    def clear(self) -> None:
        self._store.clear()

    def validate_key(self, raw_key: str) -> APIKey | None:
        self.calls += 1
        self.last_raw_key = raw_key
        return self._store.get(raw_key)
