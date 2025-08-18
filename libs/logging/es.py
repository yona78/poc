"""Elasticsearch logging handler."""

import logging
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
                "level": record.levelname,
                "message": self.format(record),
                "logger": record.name,
            }
            self.client.index(index=self.index, document=doc)
        except Exception:
            pass
