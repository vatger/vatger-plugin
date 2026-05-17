import uuid
from datetime import UTC

from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from interfaces.repositories.silent_request_repository_interface import (
    DuplicateSilentRequestException,
    SilentRequestRepositoryInterface,
)
from models.silent_request_model import SilentRequestModel


class MongoSilentRequestRepository(SilentRequestRepositoryInterface):
    def __init__(self, collection: Collection):
        self.collection = collection

        self.collection.create_index("callsign", unique=True)
        self.collection.create_index("user_id", unique=True)

    def _doc_to_request(self, doc: dict) -> SilentRequestModel:
        return SilentRequestModel(
            callsign=doc["callsign"],
            user_id=uuid.UUID(doc["user_id"]),
            departure_icao=doc["departure_icao"],
            requested_at=doc["requested_at"].replace(tzinfo=UTC),
        )

    def _request_to_doc(self, request: SilentRequestModel) -> dict:
        return {
            "callsign": request.callsign,
            "user_id": str(request.user_id),
            "departure_icao": request.departure_icao,
            "requested_at": request.requested_at,
        }

    def create_request(self, request: SilentRequestModel) -> SilentRequestModel:
        try:
            self.collection.insert_one(self._request_to_doc(request))
        except DuplicateKeyError:
            raise DuplicateSilentRequestException from None
        else:
            return request

    def get_request_by_callsign(self, callsign: str) -> SilentRequestModel | None:
        doc = self.collection.find_one({"callsign": callsign})

        if not doc:
            return None

        return self._doc_to_request(doc)

    def get_request_by_user_id(self, id: uuid.UUID) -> SilentRequestModel | None:
        doc = self.collection.find_one({"user_id": str(id)})

        if not doc:
            return None

        return self._doc_to_request(doc)

    def get_requests_by_icao(self, icao: str) -> list[SilentRequestModel] | None:
        results = [
            self._doc_to_request(doc) for doc in self.collection.find({"departure_icao": icao})
        ]

        return results or None

    def get_all_requests(self) -> list[SilentRequestModel] | None:
        docs = self.collection.find()

        if not docs:
            return None

        return [request for doc in docs if (request := self._doc_to_request(doc)) is not None]

    def delete_request_by_callsign(self, callsign: str) -> bool:
        result = self.collection.delete_one({"callsign": callsign})
        return result.deleted_count == 1
