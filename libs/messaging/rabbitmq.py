import json
import os
import threading
from typing import Callable, Dict, Any

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = os.getenv("VIDEO_METADATA_QUEUE", "video_metadata")


def start_consuming(callback: Callable[[Dict[str, Any]], None]) -> None:
    """Start a background thread that consumes messages and passes them to *callback*.

    Parameters
    ----------
    callback: Callable[[Dict[str, Any]], None]
        Function executed for each decoded message.
    """

    def _consume() -> None:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        def on_message(ch, method, properties, body):
            try:
                payload = json.loads(body)
                callback(payload)
            finally:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
        channel.start_consuming()

    thread = threading.Thread(target=_consume, daemon=True)
    thread.start()
