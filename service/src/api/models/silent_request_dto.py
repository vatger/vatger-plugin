from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SilentRequestCreateDTO(BaseModel):
    type: Literal["TAXI", "PUSHBACK"]


class SilentRequestOutDTO(BaseModel):
    callsign: str
    departure_icao: str
    type: Literal["TAXI", "PUSHBACK"]
    requested_at: datetime
