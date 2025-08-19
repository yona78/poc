"""FastAPI application for video metadata management."""

import logging

from fastapi import FastAPI

from libs.logging import ElasticsearchLogHandler, JsonFormatter
from libs.messaging.base import MessageBroker
from libs.messaging.rabbitmq import RabbitMQBroker
from libs.models.video_metadata import VideoMetadataDTO
from libs.storage.base import Storage
from libs.storage.elasticsearch import ElasticsearchStorage
from libs.storage.mongo import MongoStorage

from .settings import settings

from .controller import router
from .service import VideoMetadataService, set_service

logger = logging.getLogger("video_metadata_service")
logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

formatter = JsonFormatter()
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

es_handler = ElasticsearchLogHandler(
    settings.log_elasticsearch_url, settings.log_elasticsearch_index
)
logger.addHandler(es_handler)

app = FastAPI(title="Video Metadata Service")

storage_backend: Storage[VideoMetadataDTO] = ElasticsearchStorage(
    VideoMetadataDTO,
    host=settings.elasticsearch_url,
    index=settings.elasticsearch_index,
    id_field="video_id",
)
mongo_backend = MongoStorage(
    settings.mongodb_url,
    settings.mongodb_db,
    settings.mongodb_collection,
    id_field="video_id",
)
service = VideoMetadataService(storage_backend, mongo_backend, logger)
set_service(service)

message_broker: MessageBroker[VideoMetadataDTO] = RabbitMQBroker(
    VideoMetadataDTO,
    url=settings.rabbitmq_url,
    queue_name=settings.video_metadata_queue,
)


@app.on_event("startup")
def startup_event() -> None:
    logger.info(
        "Starting message consumption from RabbitMQ queue %s",
        settings.video_metadata_queue,
    )
    message_broker.start_consuming(service.create_from_message)


app.include_router(router)
