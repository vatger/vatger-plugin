from pydantic import BaseModel


class UserInfoDTO(BaseModel):
    cid: str
    access: bool = False
    admin: bool = False
