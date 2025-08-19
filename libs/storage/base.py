"""Abstract storage interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar


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
    def search(self, query: Dict[str, Any]) -> List[T]:
        """Search for objects matching an Elasticsearch-style *query*."""
        raise NotImplementedError

