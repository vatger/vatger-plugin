import datetime
import uuid
from typing import Literal

from core.security import generate_token
from interfaces.services.plugin_token_service_interface import PluginTokenServiceInterface
from models.plugin_token import PluginToken
from models.user import User


class InvalidTokenException(Exception): ...


class TokenAlreadyAuthorizedException(Exception): ...


class UnauthorizedException(Exception): ...


class PermissionDeniedException(Exception):
    def __init__(self, message: str = "Permission denied"):
        self.message = message
        super().__init__(message)


class PluginTokenService(PluginTokenServiceInterface):
    def __init__(self, repository):
        self.repo = repository

    def _parse_token_id(self, token_id: str) -> uuid.UUID:
        try:
            return uuid.UUID(token_id)
        except ValueError as e:
            raise InvalidTokenException from e

    def _get_valid_flow_token(self, token_id: str) -> PluginToken:
        token = self.repo.get(self._parse_token_id(token_id))

        if not token or token.user or not token.polling_secret:
            raise InvalidTokenException()

        return token

    def _get_token_or_raise(self, token_id: str) -> PluginToken:
        token = self.repo.get(self._parse_token_id(token_id))

        if not token:
            raise InvalidTokenException()

        return token

    def start_plugin_auth_flow(self) -> PluginToken:
        token = PluginToken(token=generate_token(), polling_secret=generate_token())

        return self.repo.create(token)

    def get_authorization_redirect(self, token_id: str, user: User | None) -> str:
        _ = self._get_valid_flow_token(token_id)

        url = f"/authorize-plugin/{token_id}"

        if user:
            return url
        return f"/api/v1/auth?state={url}"

    def user_authorize_plugin(self, token_id: str, user_id: str, label: str):
        token = self._get_token_or_raise(token_id)

        if not token.polling_secret:
            raise InvalidTokenException

        if token.user:
            raise TokenAlreadyAuthorizedException

        token.user = uuid.UUID(user_id)
        token.label = label
        token.last_used = datetime.datetime.now(datetime.UTC)

        return self.repo.update(token)

    def exchange_polling_secret_for_token(self, token_id: str, secret: str) -> str | None:
        token = self._get_token_or_raise(token_id)

        # token has not been authed yet
        if not token.polling_secret:
            raise InvalidTokenException()

        if not token.user:
            return None

        # incorrect secret
        if token.polling_secret != secret:
            raise UnauthorizedException

        token.polling_secret = None  # delete polling secret
        self.repo.update(token)

        return token.token

    def get_tokens(self, scope: Literal["own", "all"], user: User):
        if scope == "all":
            # user must be admin to request all tokens
            if not user.admin:
                raise PermissionDeniedException()

            return self.repo.get_tokens()

        # default to only returning the users tokens
        return self.repo.get_tokens_by_user(user.id)

    def revoke_token(self, token_id: str, user: User):
        token = self._get_token_or_raise(token_id)

        # token must belong to user if he is not an admin
        if token.user != user.id and not user.admin:
            raise PermissionDeniedException()

        self.repo.delete(token.id)
