"""Settings for the message filter service."""

from pathlib import Path

from pydantic import AnyUrl, BaseSettings


class ServiceSettings(BaseSettings):
    rabbitmq_url: AnyUrl
    source_queue: str
    algo_queue: str
    target_video_id: str
    log_elasticsearch_url: AnyUrl
    log_elasticsearch_index: str

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"
        case_sensitive = False


settings = ServiceSettings()

