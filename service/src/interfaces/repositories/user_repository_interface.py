from abc import ABC, abstractmethod

from models.user import User


class UserRepositoryInterface(ABC):
    @abstractmethod
    def get_user_by_cid(cid: int) -> User: ...

    @abstractmethod
    def add_user(user: User): ...

    @abstractmethod
    def update_user(user: User): ...
