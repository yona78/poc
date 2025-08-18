from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    """Application configuration validated from environment variables."""

    rabbitmq_url: AnyUrl
    video_metadata_queue: str

    elasticsearch_url: AnyUrl
    elasticsearch_index: str

    log_elasticsearch_url: AnyUrl
    log_elasticsearch_index: str

    mongodb_url: AnyUrl
    mongodb_db: str
    mongodb_collection: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
