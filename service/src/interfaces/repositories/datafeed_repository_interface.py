from abc import ABC, abstractmethod

from models.datafeed import ControllerModel, DatafeedModel, PilotModel


class DatafeedRepositoryInterface(ABC):
    @abstractmethod
    def update(self, feed: DatafeedModel): ...

    @abstractmethod
    def has_callsign(self, callsign: str) -> bool: ...

    @abstractmethod
    def get_pilot_by_callsign(self, callsign: str) -> PilotModel | None: ...

    @abstractmethod
    def get_pilot_by_cid(self, cid: int) -> PilotModel | None: ...

    @abstractmethod
    def has_controller(self, callsign: str) -> bool: ...

    @abstractmethod
    def get_controller_by_callsign(self, callsign: str) -> ControllerModel | None: ...

    @abstractmethod
    def get_controller_by_cid(self, cid: int) -> ControllerModel | None: ...
