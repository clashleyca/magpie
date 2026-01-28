"""Book management for magpie."""

from .models import Book, Source, SearchResult
from .db import (
    add_book,
    get_book,
    list_books,
    find_book_by_title_author,
    update_status,
    delete_book,
    add_source,
    get_source,
    get_source_by_external_id,
    list_sources,
    delete_source,
    add_book_source,
    get_book_sources,
    get_books_for_source,
    get_book_source_count,
    delete_book_sources_for_source,
)
from .extractor import BookExtractor
from .enricher import BookEnricher

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
