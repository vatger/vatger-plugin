from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


class BaseRepository[T](ABC):
    """Generic repository interface for CRUD operations."""

    @abstractmethod
    def create(self, data: T) -> T: ...

    @abstractmethod
    def get(self, id_: str) -> T | None: ...

    @abstractmethod
    def get_all(self) -> Sequence[T]: ...

    @abstractmethod
    def update(self, id_: str, data: T) -> T | None: ...

    @abstractmethod
    def delete(self, id_: str) -> bool: ...
