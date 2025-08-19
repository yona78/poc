"""Service that filters messages by video_id and forwards to an algorithm queue."""

import logging

from fastapi import FastAPI

from libs.logging import ElasticsearchLogHandler, JsonFormatter
from libs.messaging.rabbitmq import RabbitMQBroker
from libs.models.video_metadata import VideoMetadataDTO
from libs.resolvers import VideoIdResolver

from .settings import settings


logger = logging.getLogger("filter_service")
logger.setLevel(logging.INFO)

formatter = JsonFormatter()
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

es_handler = ElasticsearchLogHandler(
    settings.log_elasticsearch_url, settings.log_elasticsearch_index
)
logger.addHandler(es_handler)

app = FastAPI(title="Message Filter Service")

consumer = RabbitMQBroker(
    VideoMetadataDTO,
    url=settings.rabbitmq_url,
    queue_name=settings.source_queue,
)
publisher = RabbitMQBroker(
    VideoMetadataDTO,
    url=settings.rabbitmq_url,
    queue_name=settings.algo_queue,
)

resolver = VideoIdResolver(settings.target_video_id)


def process(message: VideoMetadataDTO) -> None:
    logger.debug(
        "Received message", extra={"labels": {"video_id": message.video_id}}
    )
    if resolver.resolve(message):
        publisher.publish(message)
        logger.info(
            "Forwarded message", extra={"labels": {"video_id": message.video_id}}
        )
    else:
        logger.info(
            "Dropped message", extra={"labels": {"video_id": message.video_id}}
        )


@app.on_event("startup")
def startup_event() -> None:
    logger.info(
        "Consuming from %s and publishing to %s",
        settings.source_queue,
        settings.algo_queue,
        extra={"labels": {"filter_video_id": settings.target_video_id}},
    )
    consumer.start_consuming(process)

