import httpx

from domain.datafeed import DatafeedModel
from interfaces.gateways.datafeed_gateway_interface import DatafeedGatewayInterface


class VatsimDatafeedGateway(DatafeedGatewayInterface):
    URL = "https://df.vatsim-germany.org/datafeed"

    async def fetch(self) -> DatafeedModel | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.URL)
            data = response.json()

        if not data:
            return None

        return DatafeedModel(**data["data"])
