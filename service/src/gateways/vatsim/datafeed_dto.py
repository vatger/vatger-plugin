from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DatafeedGeneralObjectModel(BaseModel):
    version: int
    update_timestamp: datetime
    connected_clients: int
    unique_users: int


class DatafeedPilotModel(BaseModel):
    class DatafeedPilotFlightPlanModel(BaseModel):
        flight_rules: Literal["I", "V"]
        aircraft: str
        aircraft_faa: str
        departure: str
        arrival: str
        alternate: str
        deptime: str
        enroute_time: str
        fuel_time: str
        remarks: str
        route: str
        revision_id: int
        assigned_transponder: str

    cid: int
    name: str
    callsign: str
    server: str
    pilot_rating: int
    military_rating: int
    latitude: float
    longitude: float
    altitude: int
    groundspeed: int
    transponder: str
    heading: int
    qnh_i_hg: float
    qnh_mb: int
    flight_plan: DatafeedPilotFlightPlanModel | None
    logon_time: datetime
    last_updated: datetime


class DatafeedControllerModel(BaseModel):
    cid: int
    name: str
    callsign: str
    frequency: str
    facility: int
    rating: int
    server: str
    visual_range: int
    text_atis: list[str] | None
    logon_time: datetime
    last_updated: datetime


class DatafeedModel(BaseModel):
    general: DatafeedGeneralObjectModel
    pilots: list[DatafeedPilotModel]
    controllers: list[DatafeedControllerModel]
