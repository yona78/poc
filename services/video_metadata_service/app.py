from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError

from libs.messaging.base import MessageBroker
from libs.messaging.rabbitmq import RabbitMQBroker
from libs.models.video_metadata import VideoMetadata
from libs.storage.base import Storage
from libs.storage.elasticsearch import ElasticsearchStorage

app = FastAPI(title="Video Metadata Service")

storage_backend: Storage = ElasticsearchStorage()
message_broker: MessageBroker = RabbitMQBroker()


def get_storage() -> Storage:
    return storage_backend


@app.on_event("startup")
def startup_event() -> None:
    message_broker.start_consuming(process_message)


def process_message(data: Dict[str, Any]) -> None:
    try:
        metadata = VideoMetadata(**data)
    except ValidationError:
        return
    storage_backend.create(metadata)


@app.post("/videos", response_model=VideoMetadata)
def create_video(
    metadata: VideoMetadata, storage: Storage = Depends(get_storage)
) -> VideoMetadata:
    storage.create(metadata)
    return metadata


@app.get("/videos/{video_id}", response_model=VideoMetadata)
def read_video(video_id: str, storage: Storage = Depends(get_storage)) -> VideoMetadata:
    data = storage.get(video_id)
    if not data:
        raise HTTPException(status_code=404, detail="Video metadata not found")
    return data


@app.get("/videos", response_model=List[VideoMetadata])
def list_videos(storage: Storage = Depends(get_storage)) -> List[VideoMetadata]:
    return storage.list()


@app.put("/videos/{video_id}", response_model=VideoMetadata)
def update_video(
    video_id: str, metadata: VideoMetadata, storage: Storage = Depends(get_storage)
) -> VideoMetadata:
    storage.update(video_id, metadata)
    return metadata


@app.delete("/videos/{video_id}")
def delete_video(video_id: str, storage: Storage = Depends(get_storage)) -> Dict[str, str]:
    storage.delete(video_id)
    return {"status": "deleted"}
