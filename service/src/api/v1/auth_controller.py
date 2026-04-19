from typing import TYPE_CHECKING, Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from jose import JWTError

from api.models.user_dto import UserInfoDTO
from containers.dependencies import DependencyContainer
from core.security import create_access_token, create_refresh_token, decode_token
from interfaces.repositories.user_repository_interface import UserRepositoryInterface
from models.user import User
from services.auth_service import AuthService
from settings import settings

if TYPE_CHECKING:
    from models.auth import AuthModel

router = APIRouter()


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


@inject
def get_user(
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(Provide(DependencyContainer.mongo_container.user_repository)),
    ],
    access_token: Annotated[str | None, Cookie(alias=settings.COOKIE_NAME_ACCESS)] = None,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if access_token is None:
        raise credentials_exception

    try:
        payload = decode_token(access_token)
        cid: str | None = payload.get("sub")
        if cid is None:
            raise credentials_exception

        user = user_repository.get_user_by_cid(cid)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User not found in database",
            )

        if not user.access:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    except JWTError as exc:
        raise credentials_exception from exc

    return user


@inject
def get_optional_user(
    user_repository: Annotated[
        UserRepositoryInterface,
        Depends(Provide(DependencyContainer.mongo_container.user_repository)),
    ],
    access_token: Annotated[str | None, Cookie(alias=settings.COOKIE_NAME_ACCESS)] = None,
) -> User | None:
    try:
        return get_user(user_repository=user_repository, access_token=access_token)
    except HTTPException:
        return None


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
