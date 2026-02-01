from fastapi import APIRouter

from . import v1

main_router = APIRouter(prefix="/api")
main_router.include_router(v1.router)
