import uuid
from dataclasses import dataclass


@dataclass
class User:
    id: uuid.uuid4
    cid: str
    name: str
    rating: str
    admin: bool = False
    access: bool = False
