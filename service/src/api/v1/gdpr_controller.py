from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from containers.dependencies import DependencyContainer
from interfaces.repositories.plugin_token_repository_interface import PluginTokenRepositoryInterface
from interfaces.repositories.silent_request_repository_interface import (
    SilentRequestRepositoryInterface,
)
from interfaces.repositories.user_repository_interface import UserRepositoryInterface
from interfaces.services.plugin_token_service_interface import PluginTokenServiceInterface
from settings import settings

router = APIRouter(tags=["VATGER GDPR"])

token_scheme = HTTPBearer()


@router.delete("/gdpr/{cid}", status_code=200)
@inject
def delete_user(
    bearer_token: Annotated[HTTPAuthorizationCredentials, Depends(token_scheme)],
    cid: int,
    user_repo: Annotated[
        UserRepositoryInterface,
        Depends(Provide(DependencyContainer.mongo_container.user_repository)),
    ],
    pt_repo: Annotated[
        PluginTokenRepositoryInterface,
        Depends(Provide(DependencyContainer.mongo_container.plugin_token_repository)),
    ],
    sr_repo: Annotated[
        SilentRequestRepositoryInterface,
        Depends(Provide(DependencyContainer.mongo_container.silent_request_repository)),
    ],
):
    if not settings.GDPR_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No API token configured, refusing to continue",
        )

    if bearer_token.credentials != settings.GDPR_API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = user_repo.get_user_by_cid(cid)

    if not user:
        # as defined by VATGER, return 200 if no user data exists
        return {"detail": "No user data present"}

    # delete Plugin Tokens:
    tokens = pt_repo.get_tokens_by_user(user.id)

    for token in tokens:
        pt_repo.delete(token.id)

    # delete silent requests:
    sr_repo.delete_request_by_user(user.id)

    user_repo.delete_user(user.id)


@router.get("/{cid}")
@inject
def gdpr_get_user_data(
    bearer_token: Annotated[HTTPAuthorizationCredentials, Depends(token_scheme)],
    cid: int,
    user_repo: Annotated[
        UserRepositoryInterface,
        Depends(Provide(DependencyContainer.mongo_container.user_repository)),
    ],
    pt_repo: Annotated[
        PluginTokenServiceInterface,
        Depends(Provide(DependencyContainer.mongo_container.plugin_token_repository)),
    ],
):
    if not settings.GDPR_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No API token configured, refusing to continue",
        )

    if bearer_token.credentials != settings.GDPR_API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = user_repo.get_user_by_cid(cid)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tokens = pt_repo.get_tokens_by_user(user.id)

    return {
        "user_data": user.model_dump(),
        "plugin_tokens": [token.model_dump() for token in tokens],
    }
