from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class PilotDTO(BaseModel):
    class FlightPlanDTO(BaseModel):
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
    flight_plan: FlightPlanDTO | None = None
    logon_time: datetime
    last_updated: datetime
