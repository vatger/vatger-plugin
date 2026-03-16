import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class RequestType(StrEnum):
    PUSHBACK = "PUSHBACK"
    TAXI = "TAXI"


class SilentRequestModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))

    request_type: RequestType
    callsign: str
    airport_icao: str
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC)
    )

    model_config = ConfigDict(use_enum_values=True)  # ensure that request type is dumped as str
