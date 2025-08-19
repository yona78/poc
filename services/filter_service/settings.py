"""Settings for the message filter service."""

from pathlib import Path
from typing import List

from pydantic import AnyUrl, BaseSettings, validator


class ServiceSettings(BaseSettings):
    broker_url: AnyUrl
    source_queue: str
    algo_queue: str
    target_video_ids: List[str]
    log_elasticsearch_url: AnyUrl
    log_elasticsearch_index: str

    @validator("target_video_ids", pre=True)
    def split_ids(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"
        case_sensitive = False


settings = ServiceSettings()

