from fastapi import APIRouter

from api.v1 import auth_controller, plugin_token_controller, silent_request_controller

router = APIRouter(prefix="/v1")

router.include_router(silent_request_controller.router)
router.include_router(auth_controller.router)
router.include_router(plugin_token_controller.router)
