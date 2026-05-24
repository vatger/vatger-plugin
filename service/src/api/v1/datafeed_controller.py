from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from api.guards import get_user
from api.models.datafeed_dto import PilotDTO
from containers.dependencies import DependencyContainer
from interfaces.repositories.datafeed_repository_interface import DatafeedRepositoryInterface
from models.user import User

router = APIRouter(prefix="/datafeed", tags=["Datafeed"])


@router.get("/user/pilot", response_model=PilotDTO | None)
@inject
async def get_user_pilot_data(
    user: Annotated[User, Depends(get_user)],
    datafeed_repo: Annotated[
        DatafeedRepositoryInterface,
        Depends(Provide[DependencyContainer.datafeed_container.datafeed_repository]),
    ],
):
    pilot_data = await datafeed_repo.get_pilot_by_cid(user.cid)

    if not pilot_data:
        return

    return PilotDTO(**pilot_data.model_dump())
