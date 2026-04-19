import secrets
from datetime import UTC, datetime, timedelta

from jose import jwt

from settings import settings

ALGORITHM = "HS256"


def create_access_token(cid: str, validity_minutes: int = 10) -> str:
    return jwt.encode(
        {
            "sub": cid,
            "exp": datetime.now(UTC) + timedelta(minutes=validity_minutes),
            "admin": True,
            "access": True,
        },
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_refresh_token(cid: str, validity_minutes: int = 31 * 24 * 60) -> str:
    return jwt.encode(
        {
            "sub": cid,
            "exp": datetime.now(UTC) + timedelta(minutes=validity_minutes),
        },
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def generate_token():
    return secrets.token_hex(32)
