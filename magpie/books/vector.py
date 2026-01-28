"""Vector store operations for books."""

import contextlib
from typing import Any

from chromadb.api.models.Collection import Collection


def add_book_chunk(
    collection: Collection,
    book_id: int,
    text: str,
    embedding: list[float],
    metadata: dict[str, Any] | None = None,
) -> None:
    """Add a book chunk to the vector store."""
    doc_id = f"doc_{book_id}"
    meta = metadata or {}
    meta["book_id"] = book_id

    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[meta],
    )


def search(
    collection: Collection,
    query_embedding: list[float],
    n_results: int = 10,
) -> dict[str, Any]:
    """Search for similar books by embedding."""
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )


def delete_book(collection: Collection, book_id: int) -> None:
    """Delete a book from the vector store."""
    with contextlib.suppress(Exception):
        collection.delete(ids=[f"doc_{book_id}"])
