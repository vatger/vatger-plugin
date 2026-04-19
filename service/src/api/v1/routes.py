from fastapi import APIRouter

from . import auth_controller, silent_request_controller

router = APIRouter(prefix="/v1")

router.include_router(silent_request_controller.router)
router.include_router(auth_controller.router)
