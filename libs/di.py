"""Simple dependency injection helpers."""

import inspect
import os
from typing import Any, Type

from .messaging.base import MessageBroker
from .messaging.rabbitmq import RabbitMQBroker
from .database.base import Database
from .database.elasticsearch import ElasticsearchDatabase
from .database.mongo import MongoDatabase

BROKERS = {
    "rabbitmq": RabbitMQBroker,
}

DATABASES = {
    "elasticsearch": ElasticsearchDatabase,
    "mongo": MongoDatabase,
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


def create_database(model: Type, backend: str | None = None, **kwargs: Any) -> Database:
    name = (backend or os.getenv("DATABASE_BACKEND", "elasticsearch")).lower()
    cls = DATABASES.get(name)
    if cls is None:  # pragma: no cover - defensive
        raise ValueError(f"Unknown database backend '{name}'")
    return _construct(cls, model, kwargs)
