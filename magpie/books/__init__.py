"""Book management for magpie."""

from .db import (
    add_book,
    add_book_source,
    add_source,
    delete_book,
    delete_book_sources_for_source,
    delete_source,
    find_book_by_title_author,
    get_book,
    get_book_source_count,
    get_book_sources,
    get_books_for_source,
    get_source,
    get_source_by_external_id,
    list_books,
    list_sources,
    update_status,
)
from .enricher import BookEnricher
from .extractor import BookExtractor
from .models import Book, SearchResult, Source

__all__ = [
    "Book",
    "Source",
    "SearchResult",
    "BookExtractor",
    "BookEnricher",
    "add_book",
    "get_book",
    "list_books",
    "find_book_by_title_author",
    "update_status",
    "delete_book",
    "add_source",
    "get_source",
    "get_source_by_external_id",
    "list_sources",
    "delete_source",
    "add_book_source",
    "get_book_sources",
    "get_books_for_source",
    "get_book_source_count",
    "delete_book_sources_for_source",
]
