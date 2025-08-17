from typing import List

from fastapi import FastAPI, HTTPException

from libs.messaging.rabbitmq import start_consuming
from libs.models.video_metadata import VideoMetadata
from libs.storage import elasticsearch as storage

app = FastAPI(title="Video Metadata Service")


@app.on_event("startup")
def startup_event() -> None:
    start_consuming(process_message)


def process_message(data):
    metadata = VideoMetadata(**data)
    storage.index_video(metadata)


@app.post("/videos", response_model=VideoMetadata)
def create_video(metadata: VideoMetadata) -> VideoMetadata:
    storage.index_video(metadata)
    return metadata


@app.get("/videos/{video_id}", response_model=VideoMetadata)
def read_video(video_id: str) -> VideoMetadata:
    data = storage.get_video(video_id)
    if not data:
        raise HTTPException(status_code=404, detail="Video metadata not found")
    return data


@app.get("/videos", response_model=List[VideoMetadata])
def list_videos() -> List[VideoMetadata]:
    return storage.list_videos()


@app.put("/videos/{video_id}", response_model=VideoMetadata)
def update_video(video_id: str, metadata: VideoMetadata) -> VideoMetadata:
    storage.update_video(video_id, metadata)
    return metadata


@app.delete("/videos/{video_id}")
def delete_video(video_id: str) -> dict:
    storage.delete_video(video_id)
    return {"status": "deleted"}
