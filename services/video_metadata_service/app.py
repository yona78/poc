import logging

from fastapi import FastAPI

from libs.config import settings
from libs.logging import ElasticsearchLogHandler
from libs.messaging.base import MessageBroker
from libs.messaging.rabbitmq import RabbitMQBroker
from libs.models.video_metadata import VideoMetadata, VideoMetadataDTO
from libs.storage.base import Storage
from libs.storage.elasticsearch import ElasticsearchStorage
from libs.storage.mongo import MongoStorage

from .controller import router
from .service import VideoMetadataService, set_service

logger = logging.getLogger("video_metadata_service")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(console_handler)

es_handler = ElasticsearchLogHandler(
    settings.log_elasticsearch_url, settings.log_elasticsearch_index
)
es_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(es_handler)

app = FastAPI(title="Video Metadata Service")

storage_backend: Storage[VideoMetadata] = ElasticsearchStorage(
    host=settings.elasticsearch_url,
    index=settings.elasticsearch_index,
)
mongo_backend = MongoStorage(
    settings.mongodb_url, settings.mongodb_db, settings.mongodb_collection
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
