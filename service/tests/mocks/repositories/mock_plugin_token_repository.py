import copy
import uuid

from interfaces.repositories.plugin_token_repository_interface import (
    PluginTokenRepositoryInterface,
)
from models.plugin_token import PluginToken


class MockPluginTokenRepository(PluginTokenRepositoryInterface):
    def __init__(self):
        self.tokens: dict[uuid.UUID, PluginToken] = {}

    def create(self, token: PluginToken) -> PluginToken:
        stored = copy.deepcopy(token)
        self.tokens[token.id] = stored
        return copy.deepcopy(stored)

    def get(self, id: uuid.UUID) -> PluginToken | None:
        token = self.tokens.get(id)
        return copy.deepcopy(token) if token else None

    def get_tokens(self) -> list[PluginToken]:
        return [copy.deepcopy(t) for t in self.tokens.values()]

    def get_tokens_by_user(self, user_id: uuid.UUID) -> list[PluginToken]:
        return [copy.deepcopy(t) for t in self.tokens.values() if t.user == user_id]

    def update(self, token: PluginToken) -> PluginToken | None:
        if token.id not in self.tokens:
            return None

        stored = copy.deepcopy(token)
        self.tokens[token.id] = stored
        return copy.deepcopy(stored)

    def delete(self, id: uuid.UUID) -> bool:
        if id not in self.tokens:
            return False

        del self.tokens[id]
        return True
