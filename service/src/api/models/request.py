from typing import Literal

from pydantic import BaseModel


class SilentRequestDto(BaseModel):
    request_type: Literal["PUSHBACK", "TAXI"]
    callsign: str
    airport_icao: str
