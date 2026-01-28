"""Search functionality for books."""

from ..core.sqlite import get_connection
from ..core.chroma import get_client, get_collection
from .models import Book, SearchResult
from . import db, vector, encoder


def search_books(query: str, limit: int = 10) -> list[SearchResult]:
    """Search for books by semantic query.

    Args:
        query: Search query text.
        limit: Maximum number of results.

    Returns:
        List of SearchResult objects with books and scores.
    """
    query_embedding = encoder.encode(query)

    chroma_client = get_client()
    collection = get_collection(chroma_client)

    results = vector.search(collection, query_embedding, n_results=limit)

    if not results["ids"] or not results["ids"][0]:
        return []

    conn = get_connection()
    db.ensure_tables(conn)
    search_results = []

    for doc_id, metadata, distance in zip(
        results["ids"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        book_id = metadata.get("book_id") or metadata.get("document_id")
        if not book_id:
            continue

        row = db.get_book(conn, book_id)
        if not row:
            continue

        book = Book.from_row(row)
        score = 1 - distance

        sources = db.get_book_sources(conn, book_id)
        source_titles = [s["title"] for s in sources]

        search_results.append(SearchResult(
            book=book,
            score=score,
            source_titles=source_titles,
        ))

    return search_results
