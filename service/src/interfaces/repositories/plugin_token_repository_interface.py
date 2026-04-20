import uuid
from abc import ABC, abstractmethod

from models.plugin_token import PluginToken


class PluginTokenRepositoryInterface(ABC):
    @abstractmethod
    def create(self, token: PluginToken) -> PluginToken: ...

    @abstractmethod
    def get(self, id: uuid.UUID) -> PluginToken | None: ...

    @abstractmethod
    def get_tokens(self) -> list[PluginToken]: ...

    @abstractmethod
    def get_tokens_by_user(self, user_id: uuid.UUID) -> list[PluginToken]: ...

    @abstractmethod
    def update(self, token: PluginToken) -> PluginToken | None: ...

    @abstractmethod
    def delete(self, id: uuid.UUID) -> bool: ...
