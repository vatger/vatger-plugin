from datetime import datetime
from enum import IntEnum
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

    cid: int
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


class Facility(IntEnum):
    OBS = 0
    FSS = 1
    DEL = 2
    GND = 3
    TWR = 4
    APP = 5
    CTR = 6


class ControllerModel(BaseModel):
    cid: int
    name: str
    callsign: str
    frequency: str
    facility: Facility
    rating: int
    server: str
    visual_range: int
    text_atis: list[str] | None = None
    logon_time: datetime
    last_updated: datetime

    def isObserver(self) -> bool:
        return self.facility == Facility.OBS


class DatafeedModel(BaseModel):
    pilots: list[PilotModel]
    controllers: list[ControllerModel]
