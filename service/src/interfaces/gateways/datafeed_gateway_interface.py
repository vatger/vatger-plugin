from abc import ABC, abstractmethod

from domain.datafeed import DatafeedModel


class DatafeedGatewayInterface(ABC):
    @abstractmethod
    async def fetch(self) -> DatafeedModel | None: ...
