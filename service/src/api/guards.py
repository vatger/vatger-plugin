from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Cookie, Depends, Header, HTTPException, status
from jose import JWTError

from containers.dependencies import DependencyContainer
from core.security import decode_token
from interfaces.repositories.user_repository_interface import UserRepositoryInterface
from interfaces.services.plugin_token_service_interface import PluginTokenServiceInterface
from models.plugin_token import PluginToken
from models.user import User
from services.plugin_token_service import (
    UnauthorizedException,
)
from settings import settings


@inject
def get_plugin_token(
    pt_service: Annotated[
        PluginTokenServiceInterface,
        Depends(Provide(DependencyContainer.plugin_token_service)),
    ],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> PluginToken:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if authorization is None:
        raise credentials_exception

    scheme, _, bearer_token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not bearer_token:
        raise credentials_exception

    try:
        return pt_service.get_active_token_from_bearer(bearer_token)
    except UnauthorizedException as exc:
        raise credentials_exception from exc


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
