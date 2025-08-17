"""Abstract storage interfaces."""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar


T = TypeVar("T")


class Storage(ABC, Generic[T]):
    """Abstract storage interface."""

    @abstractmethod
    def create(self, obj: T) -> None:
        """Persist *obj*."""
        raise NotImplementedError

    @abstractmethod
    def get(self, obj_id: str) -> Optional[T]:
        """Retrieve object by *obj_id*."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[T]:
        """List all stored objects."""
        raise NotImplementedError

    @abstractmethod
    def update(self, obj_id: str, obj: T) -> None:
        """Update object identified by *obj_id*."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, obj_id: str) -> None:
        """Delete object identified by *obj_id*."""
        raise NotImplementedError

