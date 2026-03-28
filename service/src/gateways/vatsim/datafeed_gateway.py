import httpx

from domain.datafeed import DatafeedModel
from interfaces.gateways.datafeed_gateway_interface import DatafeedGatewayInterface


class VatsimDatafeedGateway(DatafeedGatewayInterface):
    def __init__(self, url: str):
        self.url = url

    async def fetch(self) -> DatafeedModel | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, follow_redirects=True)
            data = response.json()

        if not data:
            return None

        if not data["data"]:
            return None

        return DatafeedModel(**data["data"])
