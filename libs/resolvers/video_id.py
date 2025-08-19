"""Resolver implementation that filters by video ID."""

from dataclasses import dataclass

from libs.models.video_metadata import VideoMetadataDTO

from .base import Resolver


@dataclass(frozen=True)
class VideoIdResolver(Resolver[VideoMetadataDTO]):
    """Allow messages that match a target ``video_id``."""

    target_video_id: str

    def resolve(self, message: VideoMetadataDTO) -> bool:
        return message.video_id == self.target_video_id
