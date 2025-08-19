import logging
from typing import Any, Dict, List, Optional

from libs.models.video_metadata import (
    EnrichedVideoMetadataDTO,
    VideoMetadataWithActionsDTO,
)
from libs.database.base import Database


class VideoMetadataService:
    """Business logic for handling video metadata operations."""

    def __init__(
        self,
        storage: Database[VideoMetadataWithActionsDTO],
        mongo: Database[Dict[str, Any]],
        logger: logging.Logger,
    ) -> None:
        self._storage = storage
        self._mongo = mongo
        self._logger = logger

    def create_from_message(self, dto: VideoMetadataWithActionsDTO) -> None:
        """Persist metadata received from the message broker."""
        self._logger.info(
            "Creating video metadata", extra={"labels": {"video_id": dto.video_id}}
        )
        self._storage.create(dto)

    def get(self, video_id: str) -> Optional[VideoMetadataWithActionsDTO]:
        return self._storage.get(video_id)

    def list(self) -> List[VideoMetadataWithActionsDTO]:
        return self._storage.list()

    def search(self, query: dict) -> List[VideoMetadataWithActionsDTO]:
        return self._storage.search(query)

    def search_with_mongo(self, query: dict) -> List[EnrichedVideoMetadataDTO]:
        results = self._storage.search(query)
        enriched: List[EnrichedVideoMetadataDTO] = []
        for dto in results:
            mongo_doc = self._mongo.get(dto.video_id)
            enriched.append(EnrichedVideoMetadataDTO(metadata=dto, mongo=mongo_doc))
        return enriched
