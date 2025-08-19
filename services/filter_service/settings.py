"""Settings for the message filter service."""

from pydantic import AnyUrl, BaseSettings


class ServiceSettings(BaseSettings):
    rabbitmq_url: AnyUrl
    source_queue: str
    algo_queue: str
    target_video_id: str
    log_elasticsearch_url: AnyUrl
    log_elasticsearch_index: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env.filter_service"
        case_sensitive = False


settings = ServiceSettings()

