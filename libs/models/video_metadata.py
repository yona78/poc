"""Domain and DTO models for video metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class Action:
    label: str
    confidence: float


@dataclass(frozen=True)
class VideoMetadata:
    video_id: str
    timestamp: datetime
    actions: List[Action]
    extra: Dict[str, Any]


class ActionDTO(BaseModel):
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)

    class Config:
        extra = "forbid"

    def to_domain(self) -> Action:
        return Action(label=self.label, confidence=self.confidence)


class VideoMetadataDTO(BaseModel):
    video_id: str = Field(..., description="Unique identifier for the video")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actions: List[ActionDTO] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"

    def to_domain(self) -> VideoMetadata:
        return VideoMetadata(
            video_id=self.video_id,
            timestamp=self.timestamp,
            actions=[a.to_domain() for a in self.actions],
            extra=self.extra,
        )

    @classmethod
    def from_domain(cls, meta: VideoMetadata) -> "VideoMetadataDTO":
        return cls(
            video_id=meta.video_id,
            timestamp=meta.timestamp,
            actions=[ActionDTO(**a.__dict__) for a in meta.actions],
            extra=meta.extra,
        )


class VideoMetadataUpdateDTO(BaseModel):
    timestamp: Optional[datetime] = None
    actions: Optional[List[ActionDTO]] = None
    extra: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"

    def apply(self, meta: VideoMetadata) -> VideoMetadata:
        return VideoMetadata(
            video_id=meta.video_id,
            timestamp=self.timestamp or meta.timestamp,
            actions=[a.to_domain() for a in self.actions] if self.actions is not None else meta.actions,
            extra=self.extra or meta.extra,
        )

