"""Resolvers for the filter service."""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List

from libs.messaging.base import MessageBroker
from libs.models.video_metadata import VideoMetadataDTO


class Resolver:
    """Resolve destinations for a message and handle forwarding."""

    def resolve(self, message: VideoMetadataDTO) -> Iterable[str]:  # pragma: no cover - interface
        raise NotImplementedError

    def handle(
        self,
        message: VideoMetadataDTO,
        publishers: Dict[str, MessageBroker[VideoMetadataDTO]],
        logger: logging.Logger,
    ) -> None:
        queues: List[str] = list(self.resolve(message))
        if not queues:
            logger.info(
                "Dropped message", extra={"labels": {"video_id": message.video_id}}
            )
            return
        for queue in queues:
            publishers[queue].publish(message, queue_name=queue)
            logger.info(
                "Forwarded message",
                extra={"labels": {"video_id": message.video_id, "queue": queue}},
            )


class VideoIdResolver(Resolver):
    """Allows only messages whose video_id is in the configured list."""

    def __init__(self, allowed_ids: Iterable[str], target_queue: str):
        self.allowed = set(allowed_ids)
        self.queue = target_queue

    def resolve(self, message: VideoMetadataDTO) -> Iterable[str]:
        if message.video_id in self.allowed:
            return [self.queue]
        return []
