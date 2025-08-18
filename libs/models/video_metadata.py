from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

class AlgorithmType(str, Enum):
    ACTION_RECOGNITION = "actionRecognition"


@dataclass(frozen=True)
class ActionRecognitionResult:
    frame_num: int
    timestamp: str
    action: str
    confidence: float
    clip_length: int


@dataclass(frozen=True)
class AlgorithmResult:
    type: AlgorithmType
    results: List[ActionRecognitionResult]


@dataclass(frozen=True)
class VideoMetadata:
    video_id: str
    timestamp: datetime
    algorithms: List[AlgorithmResult]
    extra: Dict[str, Any]


class ActionRecognitionResultDTO(BaseModel):
    frame_num: int
    timestamp: str
    action: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    clip_length: int

    class Config:
        extra = "forbid"

    def to_domain(self) -> ActionRecognitionResult:
        return ActionRecognitionResult(
            frame_num=self.frame_num,
            timestamp=self.timestamp,
            action=self.action,
            confidence=self.confidence,
            clip_length=self.clip_length,
        )


class AlgorithmResultDTO(BaseModel):
    type: AlgorithmType
    results: List[ActionRecognitionResultDTO]

    class Config:
        extra = "forbid"

    def to_domain(self) -> AlgorithmResult:
        return AlgorithmResult(
            type=self.type,
            results=[r.to_domain() for r in self.results],
        )

    @classmethod
    def from_domain(cls, algo: AlgorithmResult) -> "AlgorithmResultDTO":
        return cls(
            type=algo.type,
            results=[ActionRecognitionResultDTO(**r.__dict__) for r in algo.results],
        )


class VideoMetadataDTO(BaseModel):
    video_id: str = Field(..., description="Unique identifier for the video")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    algorithms: List[AlgorithmResultDTO] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"

    def to_domain(self) -> VideoMetadata:
        return VideoMetadata(
            video_id=self.video_id,
            timestamp=self.timestamp,
            algorithms=[a.to_domain() for a in self.algorithms],
            extra=self.extra,
        )

    @classmethod
    def from_domain(cls, meta: VideoMetadata) -> "VideoMetadataDTO":
        return cls(
            video_id=meta.video_id,
            timestamp=meta.timestamp,
            algorithms=[AlgorithmResultDTO.from_domain(a) for a in meta.algorithms],
            extra=meta.extra,
        )

class EnrichedVideoMetadataDTO(BaseModel):
    metadata: VideoMetadataDTO
    mongo: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"

class VideoMetadataUpdateDTO(BaseModel):
    timestamp: Optional[datetime] = None
    algorithms: Optional[List[AlgorithmResultDTO]] = None
    extra: Optional[Dict[str, Any]] = None

    class Config:
        extra = "forbid"

    def apply(self, meta: VideoMetadata) -> VideoMetadata:
        return VideoMetadata(
            video_id=meta.video_id,
            timestamp=self.timestamp or meta.timestamp,
            algorithms=[a.to_domain() for a in self.algorithms] if self.algorithms is not None else meta.algorithms,
            extra=self.extra or meta.extra,
        )
