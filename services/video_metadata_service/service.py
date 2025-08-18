import logging
from typing import List, Optional

from libs.models.video_metadata import (
    EnrichedVideoMetadataDTO,
    VideoMetadata,
    VideoMetadataDTO,
    VideoMetadataUpdateDTO,
)
from libs.storage.base import Storage
from libs.storage.mongo import MongoStorage


class VideoMetadataService:
    """Business logic for handling video metadata operations."""

    def __init__(
        self,
        storage: Storage[VideoMetadata],
        mongo: MongoStorage,
        logger: logging.Logger,
    ) -> None:
        self._storage = storage
        self._mongo = mongo
        self._logger = logger

    def create_from_message(self, dto: VideoMetadataDTO) -> None:
        """Persist metadata received from the message broker."""
        self._logger.info("Creating video metadata for video_id=%s", dto.video_id)
        self._storage.create(dto.to_domain())

    def get(self, video_id: str) -> Optional[VideoMetadataDTO]:
        data = self._storage.get(video_id)
        if not data:
            return None
        return VideoMetadataDTO.from_domain(data)

    def list(self) -> List[VideoMetadataDTO]:
        return [VideoMetadataDTO.from_domain(v) for v in self._storage.list()]

    def update(
        self, video_id: str, updates: VideoMetadataUpdateDTO
    ) -> Optional[VideoMetadataDTO]:
        existing = self._storage.get(video_id)
        if not existing:
            return None
        updated = updates.apply(existing)
        self._storage.update(video_id, updated)
        return VideoMetadataDTO.from_domain(updated)

    def delete(self, video_id: str) -> None:
        self._logger.info("Deleting video metadata for video_id=%s", video_id)
        self._storage.delete(video_id)

    def search(self, query: dict) -> List[VideoMetadataDTO]:
        results = self._storage.search(query)
        return [VideoMetadataDTO.from_domain(v) for v in results]

    def search_with_mongo(self, query: dict) -> List[EnrichedVideoMetadataDTO]:
        results = self._storage.search(query)
        enriched: List[EnrichedVideoMetadataDTO] = []
        for meta in results:
            mongo_doc = self._mongo.get(meta.video_id)
            enriched.append(
                EnrichedVideoMetadataDTO(
                    metadata=VideoMetadataDTO.from_domain(meta), mongo=mongo_doc
                )
            )
        return enriched


_service: Optional[VideoMetadataService] = None


def set_service(service: VideoMetadataService) -> None:
    global _service
    _service = service


def get_service() -> VideoMetadataService:
    if _service is None:  # pragma: no cover - defensive
        raise RuntimeError("Service not initialized")
    return _service
