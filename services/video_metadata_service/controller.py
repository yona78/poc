import json
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException

from libs.models.video_metadata import (
    EnrichedVideoMetadataDTO,
    VideoMetadataDTO,
    VideoMetadataUpdateDTO,
)

from .service import VideoMetadataService, get_service

router = APIRouter()


@router.get("/videos/{video_id}", response_model=VideoMetadataDTO)
def read_video(
    video_id: str, service: VideoMetadataService = Depends(get_service)
) -> VideoMetadataDTO:
    data = service.get(video_id)
    if not data:
        raise HTTPException(status_code=404, detail="Video metadata not found")
    return data


@router.get("/videos", response_model=List[VideoMetadataDTO])
def list_videos(
    service: VideoMetadataService = Depends(get_service),
) -> List[VideoMetadataDTO]:
    return service.list()


@router.put("/videos/{video_id}", response_model=VideoMetadataDTO)
def update_video(
    video_id: str,
    updates: VideoMetadataUpdateDTO,
    service: VideoMetadataService = Depends(get_service),
) -> VideoMetadataDTO:
    updated = service.update(video_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Video metadata not found")
    return updated


@router.delete("/videos/{video_id}")
def delete_video(
    video_id: str, service: VideoMetadataService = Depends(get_service)
) -> Dict[str, str]:
    service.delete(video_id)
    return {"status": "deleted"}


@router.get("/videos/search", response_model=List[VideoMetadataDTO])
def search_videos(
    query: str, service: VideoMetadataService = Depends(get_service)
) -> List[VideoMetadataDTO]:
    try:
        query_dict = json.loads(query)
    except json.JSONDecodeError as exc:  # pragma: no cover - validation
        raise HTTPException(status_code=400, detail="Invalid JSON query") from exc
    return service.search(query_dict)


@router.get("/videos/search_with_mongo", response_model=List[EnrichedVideoMetadataDTO])
def search_videos_with_mongo(
    query: str, service: VideoMetadataService = Depends(get_service)
) -> List[EnrichedVideoMetadataDTO]:
    try:
        query_dict = json.loads(query)
    except json.JSONDecodeError as exc:  # pragma: no cover - validation
        raise HTTPException(status_code=400, detail="Invalid JSON query") from exc
    return service.search_with_mongo(query_dict)
