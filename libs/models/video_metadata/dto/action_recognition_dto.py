from pydantic import BaseModel, Field

from ..types.action_recognition import ActionRecognitionResult


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

    @classmethod
    def from_domain(cls, result: ActionRecognitionResult) -> "ActionRecognitionResultDTO":
        return cls(
            frame_num=result.frame_num,
            timestamp=result.timestamp,
            action=result.action,
            confidence=result.confidence,
            clip_length=result.clip_length,
        )
