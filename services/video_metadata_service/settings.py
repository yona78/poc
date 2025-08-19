"""Settings for the video metadata service."""

from pathlib import Path

from pydantic import AnyUrl, BaseSettings


class ServiceSettings(BaseSettings):
    broker_url: AnyUrl
    video_metadata_queue: str
    elasticsearch_url: AnyUrl
    elasticsearch_index: str
    log_elasticsearch_url: AnyUrl
    log_elasticsearch_index: str
    mongodb_url: AnyUrl
    mongodb_db: str
    mongodb_collection: str

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"
        case_sensitive = False


settings = ServiceSettings()

