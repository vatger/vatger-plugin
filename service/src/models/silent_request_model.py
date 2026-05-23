import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SilentRequestModel(BaseModel):
    callsign: str
    user_id: uuid.UUID
    departure_icao: str
    type: Literal["TAXI", "PUSHBACK"]
    requested_at: datetime
