from typing import TYPE_CHECKING, Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from jose import JWTError

from api.guards import get_user
from api.models.user_dto import UserInfoDTO
from auth.auth_service import AuthService
from containers.dependencies import DependencyContainer
from core.security import create_access_token, create_refresh_token, decode_token
from models.user import User
from settings import settings

if TYPE_CHECKING:
    from auth.auth_model import AuthModel

router = APIRouter(tags=["Auth"])


def _set_auth_cookies(response: Response, access: str, refresh: str) -> None:
    """Helper to set both auth cookies consistently."""
    cookie_defaults = {"httponly": True, "secure": False, "samesite": "lax", "path": "/"}
    response.set_cookie(settings.COOKIE_NAME_ACCESS, access, **cookie_defaults)
    response.set_cookie(settings.COOKIE_NAME_REFRESH, refresh, **cookie_defaults)


@router.get(
    "/auth",
)
@inject
def start_connect_flow(
    auth_service: Annotated[
        AuthService,
        Depends(Provide(DependencyContainer.auth_service)),
    ],
    state: str | None = None,
):
    url = auth_service.get_vatsim_connect_url(state)

    return RedirectResponse(url)


@router.get("/auth/callback")
@inject
def vatsim_connect_callback(
    code: str,
    response: Response,
    auth_service: Annotated[
        AuthService,
        Depends(Provide(DependencyContainer.auth_service)),
    ],
    state: str | None = None,
):
    token: AuthModel = auth_service.authenticate(code)

    response = RedirectResponse(state) if state else RedirectResponse("/")

    _set_auth_cookies(response, token.access, token.refresh)

    return response


@router.get(
    "/auth/user",
)
def get_user_endpoint(
    user: Annotated[User, Depends(get_user)],
) -> UserInfoDTO:
    return UserInfoDTO(cid=user.cid, access=user.access, admin=user.admin)


@router.post(
    "/auth/refresh",
)
def auth_refresh(
    response: Response,
    refresh_token: Annotated[str | None, Cookie(alias=settings.COOKIE_NAME_REFRESH)] = None,
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )

    try:
        payload = decode_token(refresh_token)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from e

    cid = payload.get("sub")

    if not cid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    _set_auth_cookies(response, create_access_token(cid), create_refresh_token(cid))
