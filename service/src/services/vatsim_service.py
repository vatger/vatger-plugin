from dataclasses import dataclass

import requests
from fastapi import HTTPException
from pydantic import TypeAdapter

from settings import settings


@dataclass
class AuthResponse:
    token_type: str
    expires_in: int
    access_token: str
    refresh_token: str | None


@dataclass
class UserIdNameData:
    id: str | None
    name: str | None


@dataclass
class UserRatingData:
    id: int
    short: str
    long: str


@dataclass
class UserPersonalData:
    name_first: str
    name_last: str
    name_full: str
    email: str
    country: UserIdNameData


@dataclass
class UserVatsimData:
    region: UserIdNameData
    division: UserIdNameData
    subdivision: UserIdNameData
    rating: UserRatingData
    pilotrating: UserRatingData


@dataclass
class OAuthData:
    token_valid: bool


@dataclass
class UserData:
    cid: str
    personal: UserPersonalData
    vatsim: UserVatsimData
    oauth: OAuthData


@dataclass
class UserResponse:
    data: UserData


class VatsimService:
    BASE_URL = settings.VATSIM_AUTH_URL

    def exchange_code(self, code: str) -> AuthResponse:
        response = requests.post(
            f"{self.BASE_URL}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.VATSIM_CLIENT_ID,
                "client_secret": settings.VATSIM_CLIENT_SECRET,
                "redirect_uri": settings.VATSIM_REDIRECT_URL,
                "code": code,
            },
            timeout=10,
        )

        if response.status_code >= 400:
            raise HTTPException(400, "OAuth token exchange failed")

        return TypeAdapter(AuthResponse).validate_python(response.json())

    def get_user(self, access_token: str) -> UserResponse:
        response = requests.get(
            f"{self.BASE_URL}/{settings.VATSIM_AUTH_USERINFO_PATH}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )

        if response.status_code >= 400:
            raise HTTPException(400, "Failed to fetch user info")

        return TypeAdapter(UserResponse).validate_python(response.json())
