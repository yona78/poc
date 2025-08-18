"""Abstract message broker interfaces."""

from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class MessageBroker(ABC, Generic[T]):
    """Abstract message broker interface."""

    @abstractmethod
    def start_consuming(self, callback: Callable[[T], None]) -> None:
        """Start consuming messages, invoking *callback* for each parsed payload."""
        raise NotImplementedError

