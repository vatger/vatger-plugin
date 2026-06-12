from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from api.guards import get_user
from api.models.silent_request_dto import SilentRequestCreateDTO, SilentRequestOutDTO
from containers.dependencies import DependencyContainer
from interfaces.services.silent_request_service_interface import (
    ControllerOfflineException,
    ExistingRequestException,
    InvalidAirportExpection,
    NoExistingRequestException,
    SilentRequestServiceInterface,
    UserHasNoFlightplanException,
    UserMustBeControllerException,
    UserOfflineException,
)
from models.user import User

router = APIRouter(prefix="/silent-request", tags=["SilentRequest"])


@router.post("")
@inject
async def create_silent_request(
    user: Annotated[User, Depends(get_user)],
    request: SilentRequestCreateDTO,
    sr_service: Annotated[
        SilentRequestServiceInterface,
        Depends(Provide[DependencyContainer.silent_request_service]),
    ],
):
    try:
        await sr_service.create_request(user, request.type)
    except UserOfflineException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is offline"
        ) from None
    except UserHasNoFlightplanException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User has no flightplan"
        ) from None
    except ExistingRequestException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User has an existing request"
        ) from None
    except InvalidAirportExpection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to request at this airport"
        ) from None


@router.get("", summary="Get the user's SilentRequest")
@inject
def get_user_silent_request(
    user: Annotated[User, Depends(get_user)],
    sr_service: Annotated[
        SilentRequestServiceInterface,
        Depends(Provide[DependencyContainer.silent_request_service]),
    ],
):
    request = sr_service.get_request_by_user(user.id)

    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No request")

    return SilentRequestOutDTO(**request.model_dump())


@router.delete("", summary="Delete the user's SilentRequest")
@inject
async def delete_user_silent_request(
    user: Annotated[User, Depends(get_user)],
    sr_service: Annotated[
        SilentRequestServiceInterface,
        Depends(Provide[DependencyContainer.silent_request_service]),
    ],
):
    try:
        return await sr_service.delete_request(user)
    except NoExistingRequestException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete request, no existing request found",
        ) from None
    except (ControllerOfflineException, UserMustBeControllerException):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Couldn't delete request",
        ) from None


@router.delete("/{callsign}", summary="Delete a SilentRequest by callsign")
@inject
async def delete_request(
    user: Annotated[User, Depends(get_user)],
    sr_service: Annotated[
        SilentRequestServiceInterface,
        Depends(Provide[DependencyContainer.silent_request_service]),
    ],
    callsign: str | None = None,
) -> bool:
    try:
        return await sr_service.delete_request(user, callsign)
    except NoExistingRequestException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete request, no existing request found",
        ) from None
    except ControllerOfflineException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User must be online as controller"
        ) from None
    except UserMustBeControllerException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User must be active controller"
        ) from None
