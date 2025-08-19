"""Settings for the video metadata service."""

from pydantic import AnyUrl, BaseSettings


class ServiceSettings(BaseSettings):
    rabbitmq_url: AnyUrl
    video_metadata_queue: str
    elasticsearch_url: AnyUrl
    elasticsearch_index: str
    log_elasticsearch_url: AnyUrl
    log_elasticsearch_index: str
    mongodb_url: AnyUrl
    mongodb_db: str
    mongodb_collection: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env.video_metadata_service"
        case_sensitive = False


settings = ServiceSettings()

