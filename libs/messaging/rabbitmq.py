"""RabbitMQ message broker implementation."""

import json
import os
import threading
from typing import Callable, Optional, Type, TypeVar, Generic

import pika
from pydantic import BaseModel

from .base import MessageBroker


T = TypeVar("T", bound=BaseModel)


class RabbitMQBroker(MessageBroker[T], Generic[T]):
    """RabbitMQ implementation of the MessageBroker interface."""

    def __init__(
        self,
        model: Type[T],
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        queue_name: Optional[str] = None,
        dead_letter_queue: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        self.model = model
        self.host = host or os.getenv("BROKER_HOST", "localhost")
        self.port = port or int(os.getenv("BROKER_PORT", "5672"))
        self.username = username or os.getenv("BROKER_USER", "guest")
        self.password = password or os.getenv("BROKER_PASSWORD", "guest")
        self.queue = queue_name or os.getenv("VIDEO_METADATA_QUEUE", "default_queue")
        self.dead_letter_queue = dead_letter_queue or f"{self.queue}.dlq"
        self.max_retries = max_retries

    def _connection_params(self) -> pika.ConnectionParameters:
        credentials = pika.PlainCredentials(self.username, self.password)
        return pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=credentials
        )

    def start_consuming(self, callback: Callable[[T], None]) -> None:
        """Start a background thread that consumes messages and passes them to *callback*."""

        def _consume() -> None:
            params = self._connection_params()
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=self.queue, durable=True)

            def on_message(ch, method, properties, body) -> None:  # type: ignore[no-untyped-def]
                try:
                    payload = json.loads(body)
                    message = self.model.parse_obj(payload)
                    callback(message)
                except Exception:
                    headers = properties.headers or {}
                    attempt = int(headers.get("x-retries", 0)) + 1
                    target = self.queue if attempt < self.max_retries else self.dead_letter_queue
                    ch.basic_publish(
                        exchange="",
                        routing_key=target,
                        body=body,
                        properties=pika.BasicProperties(headers={"x-retries": attempt}),
                    )
                finally:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=self.queue, on_message_callback=on_message)
            channel.start_consuming()

        thread = threading.Thread(target=_consume, daemon=True)
        thread.start()

    def publish(
        self, message: T, queue_name: Optional[str] = None, headers: Optional[dict] = None
    ) -> None:
        target = queue_name or self.queue
        params = self._connection_params()
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=target, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=target,
            body=message.json().encode(),
            properties=pika.BasicProperties(headers=headers),
        )
        connection.close()

