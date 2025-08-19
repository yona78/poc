"""Generic MongoDB storage implementation."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from pymongo import MongoClient

from .base import Storage


T = TypeVar("T")


class MongoStorage(Storage[T], Generic[T]):
    """MongoDB-backed storage for arbitrary objects."""

    def __init__(
        self,
        url: str,
        db: str,
        collection: str,
        model: Optional[Type[BaseModel]] = None,
        id_field: str = "_id",
    ) -> None:
        self.client = MongoClient(url)
        self.collection = self.client[db][collection]
        self.model = model
        self.id_field = id_field

    def _to_dict(self, obj: T) -> Dict[str, Any]:
        if isinstance(obj, BaseModel):
            data = obj.dict()
        else:
            data = obj  # type: ignore[assignment]
        if self.id_field != "_id" and self.id_field in data:
            data["_id"] = data[self.id_field]
        return data

    def _parse(self, doc: Dict[str, Any]) -> T:
        if self.model and issubclass(self.model, BaseModel):
            return self.model.parse_obj(doc)  # type: ignore[return-value]
        return doc  # type: ignore[return-value]

    def create(self, obj: T) -> None:
        self.collection.insert_one(self._to_dict(obj))

    def get(self, obj_id: str) -> Optional[T]:
        doc = self.collection.find_one({"_id": obj_id})
        if not doc:
            return None
        return self._parse(doc)

    def list(self) -> List[T]:
        return [self._parse(d) for d in self.collection.find()]

    def update(self, obj_id: str, obj: T) -> None:
        self.collection.update_one({"_id": obj_id}, {"$set": self._to_dict(obj)}, upsert=False)

    def delete(self, obj_id: str) -> None:
        self.collection.delete_one({"_id": obj_id})

    def search(self, query: Dict[str, Any]) -> List[T]:
        return [self._parse(d) for d in self.collection.find(query)]

