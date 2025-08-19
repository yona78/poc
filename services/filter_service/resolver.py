"""Resolvers for the filter service."""

from typing import Iterable

from libs.models.video_metadata import VideoMetadataDTO


class Resolver:
    """Simple resolver interface."""

    def resolve(self, message: VideoMetadataDTO) -> bool:  # pragma: no cover - interface
        raise NotImplementedError


class VideoIdResolver(Resolver):
    """Allows only messages whose video_id is in the configured list."""

    def __init__(self, allowed_ids: Iterable[str]):
        self.allowed = set(allowed_ids)

    def resolve(self, message: VideoMetadataDTO) -> bool:
        return message.video_id in self.allowed
