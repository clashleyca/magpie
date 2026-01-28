"""Core infrastructure for magpie."""

from .chroma import get_client, get_collection
from .sqlite import get_connection

__all__ = ["get_connection", "get_client", "get_collection"]
