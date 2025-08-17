from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class MessageBroker(ABC):
    """Abstract message broker interface."""

    @abstractmethod
    def start_consuming(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Start consuming messages, invoking *callback* for each payload."""
        raise NotImplementedError
