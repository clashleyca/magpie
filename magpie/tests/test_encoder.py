"""Tests for encoder utilities."""

from magpie.books.encoder import build_book_chunk


class TestBuildBookChunk:
    """Tests for build_book_chunk function."""

    def test_basic_chunk(self):
        """Should build chunk with title and author."""
        result = build_book_chunk(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            description="",
            source_titles=[],
        )

        assert result == "The Hobbit by J.R.R. Tolkien"

    def test_chunk_with_description(self):
        """Should include description in chunk."""
        result = build_book_chunk(
            title="The Hobbit",
            author="Tolkien",
            description="A fantasy adventure novel.",
            source_titles=[],
        )

        assert "The Hobbit by Tolkien" in result
        assert "A fantasy adventure novel." in result
        assert "\n\n" in result

    def test_chunk_with_source_titles(self):
        """Should include source context in chunk."""
        result = build_book_chunk(
            title="The Hobbit",
            author="Tolkien",
            description="",
            source_titles=["Best fantasy books", "Underrated novels"],
        )

        assert "Recommended for:" in result
        assert "Best fantasy books" in result
        assert "Underrated novels" in result
        assert "Tags:" in result

    def test_full_chunk(self):
        """Should combine all parts with proper formatting."""
        result = build_book_chunk(
            title="The Hobbit",
            author="Tolkien",
            description="A classic fantasy novel.",
            source_titles=["Best books 2024"],
        )

        assert "The Hobbit by Tolkien" in result
        assert "A classic fantasy novel." in result
        assert "Recommended for: Best books 2024" in result
        assert "Tags: Best books 2024" in result
