from typing import Literal

from pydantic import BaseModel


class SilentRequest(BaseModel):
    request_type: Literal["PUSHBACK", "TAXI"]
    callsign: str
    airport_icao: str
