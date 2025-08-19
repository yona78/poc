from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from .company import Company


@dataclass(frozen=True)
class VideoMetadata:
    video_id: str
    timestamp: datetime
    company: Company
    extra: Dict[str, Any]
