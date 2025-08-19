from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .video_metadata_with_actions_dto import VideoMetadataWithActionsDTO


class EnrichedVideoMetadataDTO(BaseModel):
    metadata: VideoMetadataWithActionsDTO
    mongo: Optional[Dict[str, Any]] = Field(default=None)

    class Config:
        extra = "forbid"
