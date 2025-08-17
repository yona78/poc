from abc import ABC, abstractmethod
from typing import List, Optional

from libs.models.video_metadata import VideoMetadata


class Storage(ABC):
    """Abstract storage interface for video metadata."""

    @abstractmethod
    def create(self, metadata: VideoMetadata) -> None:
        """Persist metadata for a video."""
        raise NotImplementedError

    @abstractmethod
    def get(self, video_id: str) -> Optional[VideoMetadata]:
        """Retrieve metadata for *video_id*."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[VideoMetadata]:
        """List all stored video metadata."""
        raise NotImplementedError

    @abstractmethod
    def update(self, video_id: str, metadata: VideoMetadata) -> None:
        """Update metadata for *video_id*."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, video_id: str) -> None:
        """Delete metadata for *video_id*."""
        raise NotImplementedError
