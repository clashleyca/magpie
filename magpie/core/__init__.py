"""Core infrastructure for magpie."""

from .sqlite import get_connection
from .chroma import get_client, get_collection

__all__ = ["get_connection", "get_client", "get_collection"]
