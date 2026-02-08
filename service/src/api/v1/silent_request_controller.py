from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from api.models.request import SilentRequest
from containers.dependencies import DependencyContainer
from interfaces.services.request_service_interface import RequestServiceInterface

router = APIRouter(prefix="/request")


@router.post("")
@inject
def post_request(
    request: SilentRequest,
    request_service: Annotated[
        RequestServiceInterface,
        Depends(Provide(DependencyContainer.request_container.request_service)),
    ],
):
    print(f"received {request.callsign}")
