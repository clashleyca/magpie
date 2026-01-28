"""Tests for database operations."""

import sqlite3
import pytest

from magpie.books import db


@pytest.fixture
def db_conn():
    """Create an in-memory database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    db._init_tables(conn)
    yield conn
    conn.close()


class TestBookOperations:
    """Tests for book CRUD operations."""

    def test_add_book(self, db_conn):
        """Should add a book and return its ID."""
        book_id = db.add_book(
            db_conn,
            title="The Hobbit",
            author="J.R.R. Tolkien",
            description="A fantasy novel",
            isbn="9780547928227",
        )

        assert book_id == 1
        book = db.get_book(db_conn, book_id)
        assert book["title"] == "The Hobbit"
        assert book["author"] == "J.R.R. Tolkien"
        assert book["status"] == "new"

    def test_get_book_not_found(self, db_conn):
        """Should return None for non-existent book."""
        result = db.get_book(db_conn, 999)
        assert result is None

    def test_list_books(self, db_conn):
        """Should list all books."""
        db.add_book(db_conn, title="Book 1")
        db.add_book(db_conn, title="Book 2")

        books = db.list_books(db_conn)

        assert len(books) == 2

    def test_list_books_by_status(self, db_conn):
        """Should filter books by status."""
        book_id = db.add_book(db_conn, title="Book 1")
        db.add_book(db_conn, title="Book 2")
        db.update_status(db_conn, book_id, "reading")

        reading = db.list_books(db_conn, status="reading")
        new = db.list_books(db_conn, status="new")

        assert len(reading) == 1
        assert len(new) == 1

    def test_update_status(self, db_conn):
        """Should update book status."""
        book_id = db.add_book(db_conn, title="Test Book")

        result = db.update_status(db_conn, book_id, "reading")

        assert result is True
        book = db.get_book(db_conn, book_id)
        assert book["status"] == "reading"

    def test_find_book_by_title_author(self, db_conn):
        """Should find book by title and author (case-insensitive)."""
        db.add_book(db_conn, title="The Hobbit", author="Tolkien")

        result = db.find_book_by_title_author(db_conn, "the hobbit", "TOLKIEN")

        assert result is not None
        assert result["title"] == "The Hobbit"

    def test_find_book_by_title_only(self, db_conn):
        """Should find book by title only."""
        db.add_book(db_conn, title="The Hobbit", author="Tolkien")

        result = db.find_book_by_title_author(db_conn, "The Hobbit")

        assert result is not None

    def test_delete_book(self, db_conn):
        """Should delete a book."""
        book_id = db.add_book(db_conn, title="To Delete")

        result = db.delete_book(db_conn, book_id)

        assert result is True
        assert db.get_book(db_conn, book_id) is None


class TestSourceOperations:
    """Tests for source CRUD operations."""

    def test_add_source(self, db_conn):
        """Should add a source and return its ID."""
        source_id = db.add_source(
            db_conn,
            external_id="abc123",
            title="Best Books Thread",
            source_type="reddit",
        )

        assert source_id == 1
        source = db.get_source(db_conn, source_id)
        assert source["title"] == "Best Books Thread"

    def test_add_source_returns_existing(self, db_conn):
        """Should return existing source ID if external_id already exists."""
        id1 = db.add_source(db_conn, external_id="abc123", title="First")
        id2 = db.add_source(db_conn, external_id="abc123", title="Second")

        assert id1 == id2

    def test_get_source_by_external_id(self, db_conn):
        """Should find source by external ID."""
        db.add_source(db_conn, external_id="xyz789", title="Test Thread")

        result = db.get_source_by_external_id(db_conn, "xyz789")

        assert result is not None
        assert result["title"] == "Test Thread"

    def test_list_sources(self, db_conn):
        """Should list all sources."""
        db.add_source(db_conn, external_id="a", title="Thread 1")
        db.add_source(db_conn, external_id="b", title="Thread 2")

        sources = db.list_sources(db_conn)

        assert len(sources) == 2


class TestBookSources:
    """Tests for book-source relationship operations."""

    def test_add_book_source(self, db_conn):
        """Should record a book mention in a source."""
        book_id = db.add_book(db_conn, title="Test Book")
        source_id = db.add_source(db_conn, external_id="t1", title="Thread")

        db.add_book_source(db_conn, book_id, source_id)

        sources = db.get_book_sources(db_conn, book_id)
        assert len(sources) == 1

    def test_get_books_for_source(self, db_conn):
        """Should get all books mentioned in a source."""
        book1 = db.add_book(db_conn, title="Book 1")
        book2 = db.add_book(db_conn, title="Book 2")
        source_id = db.add_source(db_conn, external_id="t1", title="Thread")
        db.add_book_source(db_conn, book1, source_id)
        db.add_book_source(db_conn, book2, source_id)

        books = db.get_books_for_source(db_conn, source_id)

        assert len(books) == 2

    def test_get_book_source_count(self, db_conn):
        """Should count sources where a book is mentioned."""
        book_id = db.add_book(db_conn, title="Popular Book")
        s1 = db.add_source(db_conn, external_id="t1", title="Thread 1")
        s2 = db.add_source(db_conn, external_id="t2", title="Thread 2")
        db.add_book_source(db_conn, book_id, s1)
        db.add_book_source(db_conn, book_id, s2)

        count = db.get_book_source_count(db_conn, book_id)

        assert count == 2

    def test_delete_book_sources_for_source(self, db_conn):
        """Should delete all book mentions for a source."""
        book_id = db.add_book(db_conn, title="Book")
        source_id = db.add_source(db_conn, external_id="t1", title="Thread")
        db.add_book_source(db_conn, book_id, source_id)

        deleted = db.delete_book_sources_for_source(db_conn, source_id)

        assert deleted == 1
        assert db.get_book_source_count(db_conn, book_id) == 0
