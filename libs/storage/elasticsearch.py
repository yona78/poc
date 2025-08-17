import os
from typing import List, Optional

from elasticsearch import Elasticsearch

from libs.models.video_metadata import VideoMetadata

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
INDEX_NAME = os.getenv("ES_VIDEO_INDEX", "videos")

_client = Elasticsearch(ES_HOST)


def index_video(metadata: VideoMetadata) -> None:
    _client.index(index=INDEX_NAME, id=metadata.video_id, document=metadata.dict())


def get_video(video_id: str) -> Optional[VideoMetadata]:
    try:
        res = _client.get(index=INDEX_NAME, id=video_id)
    except Exception:
        return None
    source = res.get("_source")
    if not source:
        return None
    return VideoMetadata(**source)


def list_videos() -> List[VideoMetadata]:
    res = _client.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
    hits = res.get("hits", {}).get("hits", [])
    return [VideoMetadata(**hit["_source"]) for hit in hits]


def update_video(video_id: str, metadata: VideoMetadata) -> None:
    _client.index(index=INDEX_NAME, id=video_id, document=metadata.dict())


def delete_video(video_id: str) -> None:
    try:
        _client.delete(index=INDEX_NAME, id=video_id)
    except Exception:
        pass
