from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from containers.dependencies import DependencyContainer
from interfaces.services.auth_service_interface import ApiKeyAuthServiceInterface

API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(
    name=API_KEY_NAME,
)


class AuthAdapter:
    """FastAPI wrapper, checks if the provided API Key has the defined permissions"""

    def __init__(self, *permissions: str):
        self.required = set(permissions)

    @inject
    def __call__(
        self,
        api_key: str | None = Security(api_key_header),
        auth_service: Annotated[
            ApiKeyAuthServiceInterface,
            Depends(Provide(DependencyContainer.auth_service)),
        ] = None,
    ):
        if not api_key:
            raise HTTPException(401, "API key missing")

        return auth_service.authorize(api_key, self.required)
