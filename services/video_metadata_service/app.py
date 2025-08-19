"""FastAPI application for video metadata management."""

import logging

from fastapi import FastAPI

from libs.di import create_message_broker, create_database
from libs.logging import ElasticsearchLogHandler, JsonFormatter
from libs.models.video_metadata import VideoMetadataDTO

from .settings import settings

from .controller import router
from .service import VideoMetadataService, set_service

logger = logging.getLogger("video_metadata_service")
logger.setLevel(logging.INFO)

formatter = JsonFormatter()
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

es_handler = ElasticsearchLogHandler(
    settings.log_elasticsearch_url, settings.log_elasticsearch_index
)
logger.addHandler(es_handler)

app = FastAPI(title="Video Metadata Service")

primary_db = create_database(
    VideoMetadataDTO,
    backend="elasticsearch",
    host=settings.elasticsearch_url,
    index=settings.elasticsearch_index,
    id_field="video_id",
)
mongo_db = create_database(
    dict,
    backend="mongo",
    url=settings.mongodb_url,
    db=settings.mongodb_db,
    collection=settings.mongodb_collection,
    id_field="video_id",
)
service = VideoMetadataService(primary_db, mongo_db, logger)
set_service(service)

message_broker = create_message_broker(
    VideoMetadataDTO,
    url=settings.broker_url,
    queue_name=settings.video_metadata_queue,
)


@app.on_event("startup")
def startup_event() -> None:
    logger.info(
        "Starting message consumption from queue %s",
        settings.video_metadata_queue,
    )
    message_broker.start_consuming(service.create_from_message)


app.include_router(router)
