import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SilentRequestModel(BaseModel):
    request_type: Literal["PUSHBACK", "TAXI"]
    callsign: str
    airport_icao: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC)
    )
