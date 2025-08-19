import logging
from typing import Any, Dict

from libs.database.base import Database
from libs.models.video_metadata import VideoMetadataWithActionsDTO


class IngestService:
    """Persist metadata received from the message broker."""

    def __init__(
        self,
        storage: Database[VideoMetadataWithActionsDTO],
        mongo: Database[Dict[str, Any]],
        logger: logging.Logger,
    ) -> None:
        self._storage = storage
        self._mongo = mongo
        self._logger = logger

    def handle_message(self, dto: VideoMetadataWithActionsDTO) -> None:
        self._logger.info(
            "Creating video metadata", extra={"labels": {"video_id": dto.video_id}}
        )
        self._storage.create(dto)
        self._mongo.create(dto.dict())
