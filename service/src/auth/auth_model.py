from pydantic import BaseModel


class AuthModel(BaseModel):
    access: str
    refresh: str
