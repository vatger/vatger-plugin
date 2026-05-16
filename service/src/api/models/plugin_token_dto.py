import uuid
from datetime import datetime

from pydantic import BaseModel


class PluginTokenStartDTO(BaseModel):
    userRedirectUrl: str
    pollingUrl: str
    pollingSecret: str


class AuthorizePluginDTO(BaseModel):
    label: str = ""


class AuthorizePluginPollDTO(BaseModel):
    secret: str


class PollPluginTokenDTO(BaseModel):
    ready: bool
    token: str


class PluginTokenDTO(BaseModel):
    id: uuid.UUID
    user: uuid.UUID | None = None
    label: str | None = None
    token: str
    last_used: datetime


class PluginTokenIntrospectionDTO(BaseModel):
    active: bool = False
    user_id: str
    label: str | None
    last_used: datetime
