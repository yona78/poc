from typing import List

from pydantic import Field

from .action_recognition_dto import ActionRecognitionResultDTO
from .video_metadata_dto import VideoMetadataDTO
from .company_dto import CompanyDTO
from ..types.video_metadata_with_actions import VideoMetadataWithActions


class VideoMetadataWithActionsDTO(VideoMetadataDTO):
    actions: List[ActionRecognitionResultDTO] = Field(default_factory=list)

    def to_domain(self) -> VideoMetadataWithActions:
        base = super().to_domain()
        return VideoMetadataWithActions(
            video_id=base.video_id,
            timestamp=base.timestamp,
            company=base.company,
            extra=base.extra,
            actions=[a.to_domain() for a in self.actions],
        )

    @classmethod
    def from_domain(cls, meta: VideoMetadataWithActions) -> "VideoMetadataWithActionsDTO":
        return cls(
            video_id=meta.video_id,
            timestamp=meta.timestamp,
            company=CompanyDTO.from_domain(meta.company),
            extra=meta.extra,
            actions=[ActionRecognitionResultDTO.from_domain(a) for a in meta.actions],
        )
