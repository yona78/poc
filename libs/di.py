"""Simple dependency injection helpers."""

import inspect
import os
from typing import Any, Type

from .messaging.base import MessageBroker
from .messaging.rabbitmq import RabbitMQBroker
from .storage.base import Storage
from .storage.elasticsearch import ElasticsearchStorage
from .storage.mongo import MongoStorage

BROKERS = {
    "rabbitmq": RabbitMQBroker,
}

STORAGES = {
    "elasticsearch": ElasticsearchStorage,
    "mongo": MongoStorage,
}


def _construct(cls: Type, model: Type, kwargs: dict) -> Any:
    sig = inspect.signature(cls.__init__)
    params = {k: v for k, v in {"model": model, **kwargs}.items() if k in sig.parameters}
    return cls(**params)


def create_message_broker(model: Type, **kwargs: Any) -> MessageBroker:
    name = os.getenv("MESSAGE_BROKER", "rabbitmq").lower()
    cls = BROKERS.get(name)
    if cls is None:  # pragma: no cover - defensive
        raise ValueError(f"Unknown message broker '{name}'")
    return _construct(cls, model, kwargs)


def create_storage(model: Type, **kwargs: Any) -> Storage:
    name = os.getenv("STORAGE_BACKEND", "elasticsearch").lower()
    cls = STORAGES.get(name)
    if cls is None:  # pragma: no cover - defensive
        raise ValueError(f"Unknown storage backend '{name}'")
    return _construct(cls, model, kwargs)
