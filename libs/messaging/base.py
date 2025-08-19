"""Abstract message broker interfaces."""

from abc import ABC, abstractmethod
from typing import Callable, Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class MessageBroker(ABC, Generic[T]):
    """Abstract message broker interface."""

    @abstractmethod
    def start_consuming(self, callback: Callable[[T], None]) -> None:
        """Start consuming messages, invoking *callback* for each parsed payload."""
        raise NotImplementedError

    @abstractmethod
    def publish(self, message: T, queue_name: Optional[str] = None) -> None:
        """Publish *message* to the specified *queue_name*."""
        raise NotImplementedError

