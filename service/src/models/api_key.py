from dataclasses import dataclass


@dataclass
class APIKey:
    key_hash: str
    owner: str
    permissions: set[str]
    active: bool = True
