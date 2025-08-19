"""Resolver interfaces and implementations."""

from .base import Resolver
from .video_id import VideoIdResolver

__all__ = ["Resolver", "VideoIdResolver"]
