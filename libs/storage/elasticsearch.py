import os
from typing import List, Optional

from elasticsearch import Elasticsearch

from libs.models.video_metadata import VideoMetadata, VideoMetadataDTO
from .base import Storage


class ElasticsearchStorage(Storage[VideoMetadata]):
    """Elasticsearch-backed storage implementation."""

    def __init__(self, host: Optional[str] = None, index: Optional[str] = None) -> None:
        self.host = host or os.getenv("ES_HOST", "http://localhost:9200")
        self.index = index or os.getenv("ES_VIDEO_INDEX", "videos")
        self.client = Elasticsearch(self.host)

    def create(self, metadata: VideoMetadata) -> None:
        dto = VideoMetadataDTO.from_domain(metadata)
        self.client.index(index=self.index, id=metadata.video_id, document=dto.dict())

    def get(self, video_id: str) -> Optional[VideoMetadata]:
        try:
            res = self.client.get(index=self.index, id=video_id)
        except Exception:
            return None
        source = res.get("_source")
        if not source:
            return None
        return VideoMetadataDTO(**source).to_domain()

    def list(self) -> List[VideoMetadata]:
        res = self.client.search(index=self.index, body={"query": {"match_all": {}}})
        hits = res.get("hits", {}).get("hits", [])
        return [VideoMetadataDTO(**hit["_source"]).to_domain() for hit in hits]

    def update(self, video_id: str, metadata: VideoMetadata) -> None:
        dto = VideoMetadataDTO.from_domain(metadata)
        self.client.index(index=self.index, id=video_id, document=dto.dict())

    def delete(self, video_id: str) -> None:
        try:
            self.client.delete(index=self.index, id=video_id)
        except Exception:
            pass
