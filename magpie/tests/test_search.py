"""Tests for search functionality."""

import pytest


class TestSearchModule:
    """Tests for search module structure."""

    def test_search_books_import(self):
        """Should be able to import search_books."""
        from magpie.books.search import search_books
        assert callable(search_books)

    def test_search_result_model(self):
        """Should be able to create SearchResult."""
        from magpie.books.models import Book, SearchResult

        book = Book(
            id=1,
            title="Test Book",
            author="Test Author",
        )
        result = SearchResult(
            book=book,
            score=0.95,
            source_titles=["Thread 1"],
        )

        assert result.book.title == "Test Book"
        assert result.score == 0.95
        assert "Thread 1" in result.source_titles
