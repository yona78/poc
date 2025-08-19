import logging
from typing import List, Optional

from libs.models.video_metadata import (
    EnrichedVideoMetadataDTO,
    VideoMetadataDTO,
    VideoMetadataUpdateDTO,
)
from libs.storage.base import Storage
from libs.storage.mongo import MongoStorage


class VideoMetadataService:
    """Business logic for handling video metadata operations."""

    def __init__(
        self,
        storage: Storage[VideoMetadataDTO],
        mongo: MongoStorage,
        logger: logging.Logger,
    ) -> None:
        self._storage = storage
        self._mongo = mongo
        self._logger = logger

    def create_from_message(self, dto: VideoMetadataDTO) -> None:
        """Persist metadata received from the message broker."""
        self._logger.info(
            "Creating video metadata", extra={"labels": {"video_id": dto.video_id}}
        )
        self._storage.create(dto)

    def get(self, video_id: str) -> Optional[VideoMetadataDTO]:
        return self._storage.get(video_id)

    def list(self) -> List[VideoMetadataDTO]:
        return self._storage.list()

    def update(
        self, video_id: str, updates: VideoMetadataUpdateDTO
    ) -> Optional[VideoMetadataDTO]:
        existing = self._storage.get(video_id)
        if not existing:
            return None
        self._logger.info(
            "Updating video metadata", extra={"labels": {"video_id": video_id}}
        )
        updated_domain = updates.apply(existing.to_domain())
        updated = VideoMetadataDTO.from_domain(updated_domain)
        self._storage.update(video_id, updated)
        return updated

    def delete(self, video_id: str) -> None:
        self._logger.info(
            "Deleting video metadata", extra={"labels": {"video_id": video_id}}
        )
        self._storage.delete(video_id)

    def search(self, query: dict) -> List[VideoMetadataDTO]:
        return self._storage.search(query)

    def search_with_mongo(self, query: dict) -> List[EnrichedVideoMetadataDTO]:
        results = self._storage.search(query)
        enriched: List[EnrichedVideoMetadataDTO] = []
        for dto in results:
            mongo_doc = self._mongo.get(dto.video_id)
            enriched.append(EnrichedVideoMetadataDTO(metadata=dto, mongo=mongo_doc))
        return enriched


_service: Optional[VideoMetadataService] = None


def set_service(service: VideoMetadataService) -> None:
    global _service
    _service = service


def get_service() -> VideoMetadataService:
    if _service is None:  # pragma: no cover - defensive
        raise RuntimeError("Service not initialized")
    return _service
