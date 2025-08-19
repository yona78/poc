"""Simple JSON logging formatter."""

import json
import logging


class JsonFormatter(logging.Formatter):
    """Format log records as JSON with optional labels."""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "labels": getattr(record, "labels", {}),
        }
        return json.dumps(log)

