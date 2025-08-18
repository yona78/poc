import json

import os
import threading
from typing import Callable, Optional, Type, TypeVar, Generic

import pika
from pydantic import BaseModel, ValidationError

from .base import MessageBroker


T = TypeVar("T", bound=BaseModel)


class RabbitMQBroker(MessageBroker[T], Generic[T]):
    """RabbitMQ implementation of the MessageBroker interface."""

    def __init__(
        self, model: Type[T], url: Optional[str] = None, queue_name: Optional[str] = None
    ) -> None:
        self.model = model
        self.url = url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self.queue = queue_name or os.getenv("VIDEO_METADATA_QUEUE", "video_metadata")

    def start_consuming(self, callback: Callable[[T], None]) -> None:
        """Start a background thread that consumes messages and passes them to *callback*."""

        def _consume() -> None:
            params = pika.URLParameters(self.url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=self.queue, durable=True)

            def on_message(ch, method, properties, body) -> None:  # type: ignore[no-untyped-def]
                try:
                    payload = json.loads(body)
                    message = self.model.parse_obj(payload)
                except ValidationError:
                    pass
                else:
                    callback(message)
                finally:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=self.queue, on_message_callback=on_message)
            channel.start_consuming()

        thread = threading.Thread(target=_consume, daemon=True)
        thread.start()
