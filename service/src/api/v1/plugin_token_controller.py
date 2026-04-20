from typing import Annotated, Literal

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from api.models.plugin_token_dto import (
    AuthorizePluginDTO,
    AuthorizePluginPollDTO,
    PluginTokenDTO,
    PluginTokenStartDTO,
    PollPluginTokenDTO,
)
from api.v1.auth_controller import get_optional_user, get_user
from containers.dependencies import DependencyContainer
from models.user import User
from services.plugin_token_service import (
    InvalidTokenException,
    PermissionDeniedException,
    PluginTokenService,
    TokenAlreadyAuthorizedException,
    UnauthorizedException,
)
from settings import settings

router = APIRouter(prefix="/plugin-token")


@router.post("/start")
@inject
def start_plugin_token_flow(
    pt_service: Annotated[
        PluginTokenService,
        Depends(Provide(DependencyContainer.plugin_token_service)),
    ],
) -> PluginTokenStartDTO:
    token = pt_service.start_plugin_auth_flow()

    return PluginTokenStartDTO(
        userRedirectUrl=f"{settings.PUBLIC_URL}/api/v1/plugin-token/authorize/{token.id}",
        pollingUrl=f"{settings.PUBLIC_URL}/api/v1/plugin-token/poll/{token.id}",
        pollingSecret=token.polling_secret,
    )


@router.get("/authorize/{token_id}")
@inject
def start_authorize_plugin_token(
    token_id: str,
    user: Annotated[User, Depends(get_optional_user)],
    pt_service: Annotated[
        PluginTokenService,
        Depends(Provide(DependencyContainer.plugin_token_service)),
    ],
):
    try:
        redirect_url = pt_service.get_authorization_redirect(token_id, user)
        return RedirectResponse(redirect_url)
    except InvalidTokenException:
        return RedirectResponse("/forbidden")


@router.post("/authorize/{token_id}")
@inject
def authorize_plugin_token(
    token_id: str,
    body: AuthorizePluginDTO,
    user: Annotated[User, Depends(get_user)],
    pt_service: Annotated[
        PluginTokenService,
        Depends(Provide(DependencyContainer.plugin_token_service)),
    ],
):
    try:
        pt_service.user_authorize_plugin(token_id, str(user.id), body.label)
    except InvalidTokenException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        ) from None
    except TokenAlreadyAuthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token already authorized"
        ) from None


@router.post("/poll/{token_id}", response_model=PollPluginTokenDTO)
@inject
def plugin_token_poll(
    token_id: str,
    body: AuthorizePluginPollDTO,
    pt_service: Annotated[
        PluginTokenService,
        Depends(Provide(DependencyContainer.plugin_token_service)),
    ],
) -> PollPluginTokenDTO:
    try:
        token: str = pt_service.exchange_polling_secret_for_token(token_id, body.secret)
    except InvalidTokenException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        ) from None
    except UnauthorizedException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        ) from None

    if not token:
        return PollPluginTokenDTO(ready=False, token="")
    else:
        return PollPluginTokenDTO(ready=True, token=token)


@router.get("", response_model=list[PluginTokenDTO])
@inject
def get_all_tokens(
    user: Annotated[User, Depends(get_user)],
    pt_service: Annotated[
        PluginTokenService,
        Depends(Provide(DependencyContainer.plugin_token_service)),
    ],
    scope: Literal["own", "all"] = "own",
):
    try:
        tokens = pt_service.get_tokens(scope=scope, user=user)
    except PermissionDeniedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        ) from None
    else:
        return [PluginTokenDTO.model_validate(t.model_dump()) for t in tokens]


@router.delete("/{token_id}")
@inject
def revoke_token(
    token_id: str,
    user: Annotated[User, Depends(get_user)],
    pt_service: Annotated[
        PluginTokenService,
        Depends(Provide(DependencyContainer.plugin_token_service)),
    ],
):
    pt_service.revoke_token(token_id, user)
