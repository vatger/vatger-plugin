from fastapi import HTTPException, status

from domain.api_key import APIKey
from interfaces.services.api_key_service_interface import APIKeyServiceInterface
from interfaces.services.auth_service_interface import AuthorizationServiceInterface


class AuthorizationService(AuthorizationServiceInterface):
    def __init__(self, service: APIKeyServiceInterface):
        self.service = service

    def authorize(self, raw_key: str, required: set[str]) -> APIKey:
        key = self.service.validate_key(raw_key)

        if not key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )

        if not required.issubset(key.permissions) and "all" not in key.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return key
