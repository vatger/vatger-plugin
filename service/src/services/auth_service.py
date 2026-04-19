import uuid
from urllib.parse import urlencode

from fastapi import HTTPException

from core.security import create_access_token, create_refresh_token
from interfaces.repositories.user_repository_interface import UserRepositoryInterface
from models.auth import AuthModel
from models.user import User
from services.vatsim_service import UserData, VatsimService
from settings import settings


class AuthService:
    def __init__(self, vatsim_service: VatsimService, user_repo: UserRepositoryInterface):
        self.vatsim_service = vatsim_service
        self.user_repo = user_repo

    def authenticate(self, code: str) -> AuthModel:
        auth_data = self.vatsim_service.exchange_code(code)
        user_response = self.vatsim_service.get_user(auth_data.access_token)

        user_data = user_response.data

        # business rules
        if not user_data.oauth.token_valid:
            raise HTTPException(401, "Invalid VATSIM token")

        if user_data.vatsim.rating.short in ("INAC", "SUS"):
            raise HTTPException(401, "Account inactive or suspended")

        return self._upsert_user_and_generate_tokens(user_data)

    def get_vatsim_connect_url(self, state: str | None = None) -> str:
        params = {
            "client_id": settings.VATSIM_CLIENT_ID,
            "redirect_uri": settings.VATSIM_REDIRECT_URL,
            "response_type": "code",
            "scope": settings.VATSIM_AUTH_SCOPES,
        }

        if state:
            params["state"] = state

        query_string = urlencode(params)

        return f"{settings.VATSIM_AUTH_URL}/oauth/authorize?{query_string}"

    def _upsert_user_and_generate_tokens(self, user_data: UserData) -> AuthModel:
        cid = user_data.cid

        user = self.user_repo.get_user_by_cid(cid)

        if user:
            user.name = user_data.personal.name_full
            user.rating = user_data.vatsim.rating.short
            self.user_repo.update_user(user)
        else:
            user = User(
                id=uuid.uuid4(),
                cid=cid,
                name=user_data.personal.name_full,
                rating=user_data.vatsim.rating.short,
            )
            self.user_repo.add_user(user)

        return AuthModel(
            access=create_access_token(cid),
            refresh=create_refresh_token(cid),
        )
