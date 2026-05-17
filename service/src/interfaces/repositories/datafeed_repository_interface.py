from abc import ABC, abstractmethod

from models.datafeed import ControllerModel, DatafeedModel, PilotModel


class DatafeedRepositoryInterface(ABC):
    @abstractmethod
    async def update(self, feed: DatafeedModel): ...

    @abstractmethod
    async def has_pilot(self, callsign: str) -> bool: ...

    @abstractmethod
    async def get_pilot_by_callsign(self, callsign: str) -> PilotModel | None: ...

    @abstractmethod
    async def get_pilot_by_cid(self, cid: int) -> PilotModel | None: ...

    @abstractmethod
    async def has_controller(self, callsign: str) -> bool: ...

    @abstractmethod
    async def get_controller_by_callsign(self, callsign: str) -> ControllerModel | None: ...

    @abstractmethod
    async def get_controller_by_cid(self, cid: int) -> ControllerModel | None: ...
