from dataclasses import dataclass


@dataclass(frozen=True)
class ActionRecognitionResult:
    frame_num: int
    timestamp: str
    action: str
    confidence: float
    clip_length: int
