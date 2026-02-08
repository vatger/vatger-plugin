from fastapi import APIRouter

from api.models.request import SilentRequest

router = APIRouter(prefix="/request")


@router.post("")
def post_request(request: SilentRequest):
    print("received")
