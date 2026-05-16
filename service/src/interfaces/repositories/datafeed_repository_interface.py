from abc import ABC, abstractmethod

from models.datafeed import DatafeedModel, PilotModel


class DatafeedRepositoryInterface(ABC):
    @abstractmethod
    def update(self, feed: DatafeedModel): ...

    @abstractmethod
    def has_callsign(callsign: str) -> bool: ...

    @abstractmethod
    def get_pilot_data(callsign: str) -> PilotModel | None: ...
