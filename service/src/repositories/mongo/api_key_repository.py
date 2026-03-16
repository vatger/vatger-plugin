from pymongo.collection import Collection

from domain.api_key import APIKey
from interfaces.repositories.api_key_repository_interface import APIKeyRepositoryInterface


class MongoAPIKeyRepository(APIKeyRepositoryInterface):
    def __init__(self, collection: Collection):
        self._collection = collection

    def get_by_hash(self, hash_value):
        doc = self._collection.find_one({"key_hash": hash_value})

        if not doc:
            return None

        return self._to_domain(doc)

    @staticmethod
    def _to_domain(doc: dict):
        perms = doc.get("permissions") or []
        return APIKey(
            key_hash=str(doc.get("key_hash", "")),
            owner=str(doc.get("owner", "")),
            permissions=set(perms),
            active=bool(doc.get("active", True)),
        )
