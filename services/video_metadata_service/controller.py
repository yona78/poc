from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException

from libs.models.video_metadata import (
    EnrichedVideoMetadataDTO,
    VideoMetadataWithActionsDTO,
)

from .dependencies import get_service
from libs.services import VideoMetadataService

router = APIRouter()


@router.get("/videos/{video_id}", response_model=VideoMetadataWithActionsDTO)
def read_video(
    video_id: str, service: VideoMetadataService = Depends(get_service)
) -> VideoMetadataWithActionsDTO:
    data = service.get(video_id)
    if not data:
        raise HTTPException(status_code=404, detail="Video metadata not found")
    return data


@router.get("/videos", response_model=List[VideoMetadataWithActionsDTO])
def list_videos(
    service: VideoMetadataService = Depends(get_service),
) -> List[VideoMetadataWithActionsDTO]:
    return service.list()


@router.get("/videos/search", response_model=List[VideoMetadataWithActionsDTO])
def search_videos(
    query: Dict[str, Any] = Body(...),
    service: VideoMetadataService = Depends(get_service),
) -> List[VideoMetadataWithActionsDTO]:
    return service.search(query)


@router.get("/videos/search_with_mongo", response_model=List[EnrichedVideoMetadataDTO])
def search_videos_with_mongo(
    query: Dict[str, Any] = Body(...),
    service: VideoMetadataService = Depends(get_service),
) -> List[EnrichedVideoMetadataDTO]:
    return service.search_with_mongo(query)
