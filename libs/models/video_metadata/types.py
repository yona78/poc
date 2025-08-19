"""Domain models for video metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


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
