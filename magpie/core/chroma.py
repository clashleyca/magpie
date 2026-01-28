"""ChromaDB connection management."""

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

DATA_DIR = Path(__file__).parent.parent.parent / "data"
CHROMA_DIR = DATA_DIR / "chroma"


def get_client() -> chromadb.ClientAPI:
    """Get a ChromaDB client with persistent storage."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection(client: chromadb.ClientAPI, name: str = "documents") -> Collection:
    """Get or create a collection."""
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )
