"""Ingest service to consume metadata messages and store them."""
import logging

from libs.di import create_database, create_message_broker
from libs.logging import ElasticsearchLogHandler, JsonFormatter
from libs.models.video_metadata import VideoMetadataWithActionsDTO

from .service import IngestService
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
    service = IngestService(storage, mongo_db, logger)
    broker = create_message_broker(
        VideoMetadataWithActionsDTO,
        host=settings.broker_host,
        port=settings.broker_port,
        username=settings.broker_user,
        password=settings.broker_password,
        queue_name=settings.video_metadata_queue,
        dead_letter_queue=settings.dead_letter_queue,
        max_retries=3,
    )
    broker.start_consuming(service.handle_message)


if __name__ == "__main__":
    main()
