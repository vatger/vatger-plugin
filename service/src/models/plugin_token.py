import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class PluginStartData(BaseModel):
    token_id: str
    secret: str


class PluginToken(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user: uuid.UUID | None = None
    label: str | None = None
    polling_secret: str | None = None
    token: str
    last_used: datetime = Field(default_factory=lambda: datetime.now(UTC))
