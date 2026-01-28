"""Data models for books."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Book:
    """A book in the magpie system."""

    id: Optional[int] = None
    title: str = ""
    author: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    google_books_id: Optional[str] = None
    isbn: Optional[str] = None
    cover_url: Optional[str] = None
    amazon_url: Optional[str] = None
    status: str = "new"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "Book":
        """Create a Book from a database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            title=row["title"],
            author=row.get("author"),
            description=row.get("description"),
            summary=row.get("summary"),
            google_books_id=row.get("google_books_id"),
            isbn=row.get("isbn"),
            cover_url=row.get("cover_url"),
            amazon_url=row.get("amazon_url"),
            status=row.get("status", "new"),
            metadata={},
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )


@dataclass
class Source:
    """A content source (Reddit thread, etc.)."""

    id: Optional[int] = None
    source_type: str = "reddit"
    external_id: str = ""
    title: str = ""
    url: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "Source":
        """Create a Source from a database row."""
        if row is None:
            return None
        return cls(
            id=row["id"],
            source_type=row.get("source_type", "reddit"),
            external_id=row["external_id"],
            title=row["title"],
            url=row.get("url"),
            metadata={},
            created_at=row.get("created_at"),
        )


@dataclass
class SearchResult:
    """A search result with book and similarity score."""

    book: Book
    score: float
    source_titles: list[str] = field(default_factory=list)
