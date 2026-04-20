import uuid

from pymongo import ReturnDocument
from pymongo.collection import Collection

from interfaces.repositories.plugin_token_repository_interface import PluginTokenRepositoryInterface
from models.plugin_token import PluginToken


class MongoPluginTokenRepository(PluginTokenRepositoryInterface):
    def __init__(self, collection: Collection):
        self.collection = collection

        self.collection.create_index("id", unique=True)

    def _doc_to_token(self, doc: dict) -> PluginToken | None:
        if not doc:
            return None

        return PluginToken(
            id=uuid.UUID(doc["id"]),
            user=uuid.UUID(doc["user"]) if doc.get("user") else None,
            label=doc.get("label"),
            polling_secret=doc.get("polling_secret"),
            token=doc.get("token"),
            last_used=doc.get("last_used"),
        )

    def _token_to_doc(self, token: PluginToken) -> dict:
        return {
            "id": str(token.id),
            "user": str(token.user) if token.user else None,
            "label": token.label,
            "polling_secret": token.polling_secret,
            "token": token.token,
            "last_used": token.last_used,
        }

    def create(self, token: PluginToken):
        result = self.collection.insert_one(self._token_to_doc(token))

        doc = self.collection.find_one({"_id": result.inserted_id})

        return self._doc_to_token(doc)

    def get(self, id: uuid.UUID) -> PluginToken | None:
        doc = self.collection.find_one({"id": str(id)})

        return self._doc_to_token(doc)

    def get_tokens(self) -> list[PluginToken]:
        docs = self.collection.find()

        return [token for doc in docs if (token := self._doc_to_token(doc)) is not None]

    def get_tokens_by_user(self, user_id: uuid.UUID) -> list[PluginToken]:
        docs = self.collection.find({"user": str(user_id)})

        return [token for doc in docs if (token := self._doc_to_token(doc)) is not None]

    def update(self, token: PluginToken) -> PluginToken | None:
        doc = self._token_to_doc(token)

        result = self.collection.find_one_and_replace(
            {"id": str(token.id)},
            doc,
            return_document=ReturnDocument.AFTER,
        )

        return self._doc_to_token(result)

    def delete(self, id: uuid.UUID) -> bool:
        result = self.collection.delete_one({"id": str(id)})
        return result.deleted_count == 1
