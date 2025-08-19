"""Ingest service to consume metadata messages and store them."""
import logging

from libs.di import create_database, create_message_broker
from libs.logging import ElasticsearchLogHandler, JsonFormatter
from libs.models.video_metadata import VideoMetadataWithActionsDTO
from libs.services import VideoMetadataService

from .settings import settings


def main() -> None:
    """Configure dependencies and start consuming messages."""
    logger = logging.getLogger("ingest_service")
    if not logger.handlers:
        formatter = JsonFormatter()
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)
        es_handler = ElasticsearchLogHandler(
            settings.log_elasticsearch_url, settings.log_elasticsearch_index
        )
        logger.addHandler(es_handler)
        logger.setLevel(logging.INFO)

    storage = create_database(
        VideoMetadataWithActionsDTO,
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
    service = VideoMetadataService(storage, mongo_db, logger)
    broker = create_message_broker(
        VideoMetadataWithActionsDTO,
        url=settings.broker_url,
        queue_name=settings.video_metadata_queue,
    )
    broker.start_consuming(service.create_from_message)


if __name__ == "__main__":
    main()
