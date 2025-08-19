"""Abstract resolver interface."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Resolver(ABC, Generic[T]):
    """Determines whether a message should be processed."""

    @abstractmethod
    def resolve(self, message: T) -> bool:
        """Return ``True`` if *message* should be forwarded."""
        raise NotImplementedError
