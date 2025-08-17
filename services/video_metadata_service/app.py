"""FastAPI application for video metadata management."""

from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException

from libs.messaging.base import MessageBroker
from libs.messaging.rabbitmq import RabbitMQBroker
from libs.models.video_metadata import (
    VideoMetadata,
    VideoMetadataDTO,
    VideoMetadataUpdateDTO,
)
from libs.storage.base import Storage
from libs.storage.elasticsearch import ElasticsearchStorage

app = FastAPI(title="Video Metadata Service")

storage_backend: Storage[VideoMetadata] = ElasticsearchStorage()
message_broker: MessageBroker[VideoMetadataDTO] = RabbitMQBroker(VideoMetadataDTO)


def get_storage() -> Storage[VideoMetadata]:
    return storage_backend


@app.on_event("startup")
def startup_event() -> None:
    message_broker.start_consuming(process_message)


def process_message(dto: VideoMetadataDTO) -> None:
    storage_backend.create(dto.to_domain())


@app.post("/videos", response_model=VideoMetadataDTO)
def create_video(
    metadata: VideoMetadataDTO, storage: Storage[VideoMetadata] = Depends(get_storage)
) -> VideoMetadataDTO:
    storage.create(metadata.to_domain())
    return metadata


@app.get("/videos/{video_id}", response_model=VideoMetadataDTO)
def read_video(
    video_id: str, storage: Storage[VideoMetadata] = Depends(get_storage)
) -> VideoMetadataDTO:
    data = storage.get(video_id)
    if not data:
        raise HTTPException(status_code=404, detail="Video metadata not found")
    return VideoMetadataDTO.from_domain(data)


@app.get("/videos", response_model=List[VideoMetadataDTO])
def list_videos(storage: Storage[VideoMetadata] = Depends(get_storage)) -> List[VideoMetadataDTO]:
    return [VideoMetadataDTO.from_domain(v) for v in storage.list()]


@app.put("/videos/{video_id}", response_model=VideoMetadataDTO)
def update_video(
    video_id: str,
    updates: VideoMetadataUpdateDTO,
    storage: Storage[VideoMetadata] = Depends(get_storage),
) -> VideoMetadataDTO:
    existing = storage.get(video_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Video metadata not found")
    updated = updates.apply(existing)
    storage.update(video_id, updated)
    return VideoMetadataDTO.from_domain(updated)


@app.delete("/videos/{video_id}")
def delete_video(video_id: str, storage: Storage[VideoMetadata] = Depends(get_storage)) -> Dict[str, str]:
    storage.delete(video_id)
    return {"status": "deleted"}
