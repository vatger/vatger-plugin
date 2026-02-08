from abc import ABC

from interfaces.repositories.base_repository import BaseRepository
from models.request import SilentRequestModel


class RequestRepositoryInterface(BaseRepository[SilentRequestModel], ABC): ...
