import logging
from typing import Any, Dict, List, Optional

from libs.database.base import Database
from libs.models.video_metadata import (
    EnrichedVideoMetadataDTO,
    VideoMetadataWithActionsDTO,
)


class VideoMetadataService:
    """Business logic for serving video metadata to clients."""

    def __init__(
        self,
        storage: Database[VideoMetadataWithActionsDTO],
        mongo: Database[Dict[str, Any]],
        logger: logging.Logger,
    ) -> None:
        self._storage = storage
        self._mongo = mongo
        self._logger = logger

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
