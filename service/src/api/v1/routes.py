from fastapi import APIRouter

from . import silent_request_controller

router = APIRouter(prefix="/v1")

router.include_router(silent_request_controller.router)
