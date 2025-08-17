import os
from typing import List, Optional

from elasticsearch import Elasticsearch

from libs.models.video_metadata import VideoMetadata
from .base import Storage


class ElasticsearchStorage(Storage):
    """Elasticsearch-backed storage implementation."""

    def __init__(self, host: Optional[str] = None, index: Optional[str] = None) -> None:
        self.host = host or os.getenv("ES_HOST", "http://localhost:9200")
        self.index = index or os.getenv("ES_VIDEO_INDEX", "videos")
        self.client = Elasticsearch(self.host)

    def create(self, metadata: VideoMetadata) -> None:
        self.client.index(index=self.index, id=metadata.video_id, document=metadata.dict())

    def get(self, video_id: str) -> Optional[VideoMetadata]:
        try:
            res = self.client.get(index=self.index, id=video_id)
        except Exception:
            return None
        source = res.get("_source")
        if not source:
            return None
        return VideoMetadata(**source)

    def list(self) -> List[VideoMetadata]:
        res = self.client.search(index=self.index, body={"query": {"match_all": {}}})
        hits = res.get("hits", {}).get("hits", [])
        return [VideoMetadata(**hit["_source"]) for hit in hits]

    def update(self, video_id: str, metadata: VideoMetadata) -> None:
        self.client.index(index=self.index, id=video_id, document=metadata.dict())

    def delete(self, video_id: str) -> None:
        try:
            self.client.delete(index=self.index, id=video_id)
        except Exception:
            pass
