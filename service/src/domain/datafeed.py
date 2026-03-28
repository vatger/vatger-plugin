from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class PilotModel(BaseModel):
    class FlightPlanModel(BaseModel):
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

    callsign: str
    latitude: float
    longitude: float
    altitude: int
    groundspeed: int
    heading: int
    qnh_i_hg: float
    qnh_mb: int
    flight_plan: FlightPlanModel | None = None
    logon_time: datetime
    last_updated: datetime


class ControllerModel(BaseModel):
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
    pilots: list[PilotModel]
    controllers: list[ControllerModel]
