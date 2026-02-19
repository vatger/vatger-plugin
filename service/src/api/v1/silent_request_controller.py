from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.adapters.auth_adapter import AuthAdapter
from api.models.request import SilentRequest
from containers.dependencies import DependencyContainer
from interfaces.repositories.request_repository_interface import DuplicateSilentRequestException
from interfaces.services.request_service_interface import RequestServiceInterface
from models.request import SilentRequestModel

router = APIRouter(prefix="/request")

RequestWrite = AuthAdapter("request:write")
RequestDelete = AuthAdapter("request:delete")


@router.get("")
@inject
def get_all_requests(
    request_service: Annotated[
        RequestServiceInterface,
        Depends(Provide(DependencyContainer.request_container.request_service)),
    ],
):
    return request_service.get_all_requests()


@router.get("/{callsign}")
@inject
def get_request(
    callsign: str,
    request_service: Annotated[
        RequestServiceInterface,
        Depends(Provide(DependencyContainer.request_container.request_service)),
    ],
):
    return request_service.get_request_by_callsign(callsign)


@router.post("", dependencies=[Depends(RequestWrite)])
@inject
def post_request(
    request: SilentRequest,
    request_service: Annotated[
        RequestServiceInterface,
        Depends(Provide(DependencyContainer.request_container.request_service)),
    ],
):
    request = SilentRequestModel(**request.model_dump())

    try:
        request_service.create_request(request)
    except DuplicateSilentRequestException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A request for this callsign already exists.",
        ) from None


@router.delete("/{callsign}", dependencies=[Depends(RequestDelete)])
@inject
def delete_request(
    callsign: str,
    request_service: Annotated[
        RequestServiceInterface,
        Depends(Provide(DependencyContainer.request_container.request_service)),
    ],
):
    request_service.delete_request_by_callsign(callsign)
