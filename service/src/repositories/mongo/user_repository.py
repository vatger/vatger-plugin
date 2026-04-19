import uuid

from pymongo.collection import Collection

from interfaces.repositories.user_repository_interface import UserRepositoryInterface
from models.user import User


class UserAlreadyExistsError(Exception):
    def __init__(self, cid: int):
        super().__init__(f"User with cid {cid} already exists")
        self.cid = cid


class MongoUserRepository(UserRepositoryInterface):
    def __init__(self, collection: Collection):
        self.collection = collection

        self.collection.create_index("cid", unique=True)

    def _doc_to_user(self, doc: dict) -> User:
        return User(
            id=uuid.UUID(doc["id"]),
            cid=doc["cid"],
            name=doc["name"],
            rating=doc["rating"],
            admin=doc.get("admin", False),
            access=doc.get("access", False),
        )

    def _user_to_doc(self, user: User) -> dict:
        return {
            "id": str(user.id),
            "cid": user.cid,
            "name": user.name,
            "rating": user.rating,
            "admin": user.admin,
            "access": user.access,
        }

    def get_user_by_cid(self, cid: int) -> User | None:
        doc = self.collection.find_one({"cid": cid})
        if not doc:
            return None
        return self._doc_to_user(doc)

    def add_user(self, user: User):
        existing = self.collection.find_one({"cid": user.cid})

        if existing:
            raise UserAlreadyExistsError(user.cid)

        doc = self._user_to_doc(user)
        self.collection.insert_one(doc)

    def update_user(self, user: User):
        doc = self._user_to_doc(user)
        result = self.collection.update_one({"cid": user.cid}, {"$set": doc})

        if result.matched_count == 0:
            msg = f"User with cid {user.cid} not found"
            raise ValueError(msg)
