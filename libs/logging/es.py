"""Elasticsearch logging handler."""

import logging
from datetime import datetime
from typing import Any, Dict

from elasticsearch import Elasticsearch


class ElasticsearchLogHandler(logging.Handler):
    """Logging handler that ships logs to Elasticsearch."""

    def __init__(self, url: str, index: str) -> None:
        super().__init__()
        self.client = Elasticsearch(url)
        self.index = index

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - best effort
        try:
            doc: Dict[str, Any] = {
                "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "labels": getattr(record, "labels", {}),
            }
            self.client.index(index=self.index, document=doc)
        except Exception:
            pass
