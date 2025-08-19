from dataclasses import dataclass, field
from typing import List

from .action_recognition import ActionRecognitionResult
from .video_metadata import VideoMetadata


@dataclass(frozen=True)
class VideoMetadataWithActions(VideoMetadata):
    actions: List[ActionRecognitionResult] = field(default_factory=list)
