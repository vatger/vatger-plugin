from interfaces.repositories.datafeed_repository_interface import DatafeedRepositoryInterface
from models.datafeed import ControllerModel, DatafeedModel, PilotModel


class MockDatafeedRepository(DatafeedRepositoryInterface):
    def __init__(
        self,
        initial_pilots: dict[str, PilotModel] | None = None,
        initial_controllers: dict[str, ControllerModel] | None = None,
    ):
        self._pilots: dict[str, PilotModel] = {}
        self._controllers: dict[str, ControllerModel] = {}
        if initial_pilots:
            self._pilots: dict[str, PilotModel] = initial_pilots

        if initial_controllers:
            self._controllers: dict[str, ControllerModel] = initial_controllers

    async def update(self, feed: DatafeedModel):
        self._pilots = {p.callsign: p for p in feed.pilots}
        self._controllers = {c.callsign: c for c in feed.controllers}

    async def has_pilot(self, callsign: str) -> bool:
        return callsign in self._pilots

    async def get_pilot_by_callsign(self, callsign: str) -> PilotModel | None:
        return self._pilots.get(callsign)

    async def get_pilot_by_cid(self, cid: int) -> PilotModel | None:
        return next((p for p in self._pilots.values() if p.cid == cid), None)

    async def has_controller(self, callsign: str) -> bool:
        return callsign in self._controllers

    async def get_controller_by_callsign(self, callsign: str) -> ControllerModel | None:
        return self._controllers.get(callsign)

    async def get_controller_by_cid(self, cid: int) -> ControllerModel | None:
        return next((c for c in self._controllers.values() if c.cid == cid), None)

    def add_pilot(self, pilot: PilotModel):
        self._pilots[pilot.callsign] = pilot

    def add_controller(self, controller: ControllerModel):
        self._controllers[controller.callsign] = controller
