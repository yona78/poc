"""Settings for the ingest service."""

from pathlib import Path

from pydantic import BaseSettings


class ServiceSettings(BaseSettings):
    broker_url: str
    video_metadata_queue: str
    elasticsearch_url: str
    elasticsearch_index: str
    log_elasticsearch_url: str
    log_elasticsearch_index: str
    mongodb_url: str
    mongodb_db: str
    mongodb_collection: str

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"
        case_sensitive = False


settings = ServiceSettings()
