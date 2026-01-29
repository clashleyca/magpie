"""Data models for books."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Book:
    """A book in the magpie system."""

    id: int | None = None
    title: str = ""
    author: str | None = None
    description: str | None = None
    summary: str | None = None
    google_books_id: str | None = None
    isbn: str | None = None
    cover_url: str | None = None
    amazon_url: str | None = None
    status: str = "new"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_row(cls, row) -> "Book":
        """Create a Book from a database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            title=row["title"],
            author=row["author"],
            description=row["description"],
            summary=row["summary"],
            google_books_id=row["google_books_id"],
            isbn=row["isbn"],
            cover_url=row["cover_url"],
            amazon_url=row["amazon_url"],
            status=row["status"] or "new",
            metadata={},
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


@dataclass
class Source:
    """A content source (Reddit thread, etc.)."""

    id: int | None = None
    source_type: str = "reddit"
    external_id: str = ""
    title: str = ""
    url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None

    @classmethod
    def from_row(cls, row) -> "Source":
        """Create a Source from a database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            source_type=row["source_type"] or "reddit",
            external_id=row["external_id"],
            title=row["title"],
            url=row["url"],
            metadata={},
            created_at=row["created_at"],
        )


@dataclass
class SearchResult:
    """A search result with book and similarity score."""

    book: Book
    score: float
    source_titles: list[str] = field(default_factory=list)
