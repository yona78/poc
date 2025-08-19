"""Service that filters messages by video_id and forwards to an algorithm queue."""

import logging

from fastapi import FastAPI

from libs.di import create_message_broker
from libs.logging import ElasticsearchLogHandler, JsonFormatter
from libs.models.video_metadata import VideoMetadataDTO

from .resolver import VideoIdResolver

from .settings import settings


app = FastAPI(title="Message Filter Service")


def _configure_logger() -> logging.Logger:
    logger = logging.getLogger("filter_service")
    if not logger.handlers:
        formatter = JsonFormatter()
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        es_handler = ElasticsearchLogHandler(
            settings.log_elasticsearch_url, settings.log_elasticsearch_index
        )
        logger.addHandler(es_handler)
        logger.setLevel(logging.INFO)
    return logger


@app.on_event("startup")
def startup_event() -> None:
    logger = _configure_logger()
    broker_kwargs = dict(
        host=settings.broker_host,
        port=settings.broker_port,
        username=settings.broker_user,
        password=settings.broker_password,
    )
    consumer = create_message_broker(
        VideoMetadataDTO,
        queue_name=settings.source_queue,
        dead_letter_queue=settings.dead_letter_queue,
        max_retries=3,
        **broker_kwargs,
    )
    publisher = create_message_broker(
        VideoMetadataDTO,
        queue_name=settings.algo_queue,
        **broker_kwargs,
    )
    resolver = VideoIdResolver(settings.target_video_ids, settings.algo_queue)

    app.state.logger = logger
    app.state.consumer = consumer
    app.state.publisher = publisher
    app.state.resolver = resolver

    publishers = {settings.algo_queue: publisher}

    def process(message: VideoMetadataDTO) -> None:
        logger.debug(
            "Received message", extra={"labels": {"video_id": message.video_id}}
        )
        resolver.handle(message, publishers, logger)

    logger.info(
        "Consuming from %s and publishing to %s",
        settings.source_queue,
        settings.algo_queue,
        extra={"labels": {"filter_video_ids": settings.target_video_ids}},
    )
    consumer.start_consuming(process)

