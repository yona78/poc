"""ECS-compatible JSON logging formatter."""

import json
import logging


class JsonFormatter(logging.Formatter):
    """Format log records as ECS JSON with optional labels."""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "@timestamp": self.formatTime(record),
            "message": record.getMessage(),
            "log": {"level": record.levelname, "logger": record.name},
            "labels": getattr(record, "labels", {}),
        }
        return json.dumps(log)

