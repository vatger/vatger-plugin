import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class SilentRequestModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))

    request_type: Literal["PUSHBACK", "TAXI"]
    callsign: str
    airport_icao: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC)
    )
