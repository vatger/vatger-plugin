from abc import ABC, abstractmethod

from domain.datafeed import DatafeedModel


class DatafeedRepositoryInterface(ABC):
    @abstractmethod
    def update(self, feed: DatafeedModel): ...

    @abstractmethod
    def get(self) -> DatafeedModel | None: ...
