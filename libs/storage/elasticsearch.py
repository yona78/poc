"""Generic Elasticsearch-backed storage implementation."""

import os
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from elasticsearch import Elasticsearch
from pydantic import BaseModel

from .base import Storage


T = TypeVar("T", bound=BaseModel)


class ElasticsearchStorage(Storage[T], Generic[T]):
    """Elasticsearch-backed storage for arbitrary Pydantic models."""

    def __init__(
        self,
        model: Type[T],
        host: Optional[str] = None,
        index: Optional[str] = None,
        id_field: str = "id",
    ) -> None:
        self.model = model
        self.host = host or os.getenv("ES_HOST", "http://localhost:9200")
        self.index = index or os.getenv("ES_INDEX", "documents")
        self.id_field = id_field
        self.client = Elasticsearch(self.host)

    def _obj_id(self, obj: T) -> str:
        return getattr(obj, self.id_field)

    def create(self, obj: T) -> None:
        self.client.index(index=self.index, id=self._obj_id(obj), document=obj.dict())

    def get(self, obj_id: str) -> Optional[T]:
        try:
            res = self.client.get(index=self.index, id=obj_id)
        except Exception:
            return None
        source = res.get("_source")
        if not source:
            return None
        return self.model.parse_obj(source)

    def list(self) -> List[T]:
        res = self.client.search(index=self.index, body={"query": {"match_all": {}}})
        hits = res.get("hits", {}).get("hits", [])
        return [self.model.parse_obj(hit["_source"]) for hit in hits]

    def search(self, query: Dict[str, Any]) -> List[T]:
        res = self.client.search(index=self.index, body=query)
        hits = res.get("hits", {}).get("hits", [])
        return [self.model.parse_obj(hit["_source"]) for hit in hits]

