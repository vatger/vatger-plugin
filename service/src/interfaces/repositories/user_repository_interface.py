import uuid
from abc import ABC, abstractmethod

from models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_user(self, id: uuid.UUID) -> User: ...

    @abstractmethod
    def get_user_by_cid(self, cid: int) -> User: ...

    @abstractmethod
    def add_user(self, user: User): ...

    @abstractmethod
    def update_user(self, user: User): ...
