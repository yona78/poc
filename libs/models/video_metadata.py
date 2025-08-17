from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Action(BaseModel):
    label: str
    confidence: float


class VideoMetadata(BaseModel):
    video_id: str = Field(..., description="Unique identifier for the video")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actions: List[Action] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)
