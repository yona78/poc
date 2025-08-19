from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field

from .company_dto import CompanyDTO
from ..types.video_metadata import VideoMetadata


class VideoMetadataDTO(BaseModel):
    video_id: str = Field(..., description="Unique identifier for the video")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    company: CompanyDTO
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"

    def to_domain(self) -> VideoMetadata:
        return VideoMetadata(
            video_id=self.video_id,
            timestamp=self.timestamp,
            company=self.company.to_domain(),
            extra=self.extra,
        )

    @classmethod
    def from_domain(cls, meta: VideoMetadata) -> "VideoMetadataDTO":
        return cls(
            video_id=meta.video_id,
            timestamp=meta.timestamp,
            company=CompanyDTO.from_domain(meta.company),
            extra=meta.extra,
        )
