import uuid
from datetime import datetime

from pydantic import BaseModel


class SilentRequestModel(BaseModel):
    callsign: str
    user_id: uuid.UUID
    departure_icao: str
    requested_at: datetime
