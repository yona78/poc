"""MongoDB storage implementation."""

from typing import Any, Dict, List, Optional

from pymongo import MongoClient

from .base import Storage


class MongoStorage(Storage[Dict[str, Any]]):
    def __init__(self, url: str, db: str, collection: str) -> None:
        self.client = MongoClient(url)
        self.collection = self.client[db][collection]

    def create(self, obj: Dict[str, Any]) -> None:
        self.collection.insert_one(obj)

    def get(self, obj_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"_id": obj_id})

    def list(self) -> List[Dict[str, Any]]:
        return list(self.collection.find())

    def update(self, obj_id: str, obj: Dict[str, Any]) -> None:
        self.collection.update_one({"_id": obj_id}, {"$set": obj}, upsert=False)

    def delete(self, obj_id: str) -> None:
        self.collection.delete_one({"_id": obj_id})

    def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        return list(self.collection.find(query))
