import logging
from fastapi import Request

from libs.di import create_database, create_message_broker
from libs.logging import ElasticsearchLogHandler, JsonFormatter
from libs.models.video_metadata import VideoMetadataDTO

from .service import VideoMetadataService
from .settings import settings


def get_logger() -> logging.Logger:
    """Configure and return a service logger."""
    logger = logging.getLogger("video_metadata_service")
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


def init_app(app) -> None:
    """Initialize and wire service dependencies."""
    logger = get_logger()
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
    app.state.service = service

    broker = create_message_broker(
        VideoMetadataDTO,
        url=settings.broker_url,
        queue_name=settings.video_metadata_queue,
    )
    broker.start_consuming(service.create_from_message)
    app.state.broker = broker


def get_service(request: Request) -> VideoMetadataService:
    """Retrieve the video metadata service from the application state."""
    return request.app.state.service
