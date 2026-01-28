"""Tests for book handlers."""

from magpie.books.enricher import _build_amazon_url, _extract_isbn
from magpie.books.extractor import _filter_valid_books


class TestFilterValidBooks:
    """Tests for _filter_valid_books function."""

    def test_filters_empty_titles(self):
        """Should remove books with empty titles."""
        books = [
            {"title": "Valid Book", "author": "Author"},
            {"title": "", "author": "Author"},
            {"title": None, "author": "Author"},
        ]

        result = _filter_valid_books(books)

        assert len(result) == 1
        assert result[0]["title"] == "Valid Book"

    def test_filters_invalid_title_values(self):
        """Should remove books with placeholder titles like 'null' or 'unknown'."""
        books = [
            {"title": "Real Book", "author": "Author"},
            {"title": "null", "author": "Author"},
            {"title": "Unknown", "author": "Author"},
            {"title": "N/A", "author": "Author"},
            {"title": "none", "author": "Author"},
        ]

        result = _filter_valid_books(books)

        assert len(result) == 1
        assert result[0]["title"] == "Real Book"

    def test_validates_against_source_text(self):
        """Should filter books whose titles don't appear in source text."""
        books = [
            {"title": "The Hobbit", "author": "Tolkien"},
            {"title": "Hallucinated Book", "author": "Fake Author"},
        ]
        source = "I really loved The Hobbit when I was young."

        result = _filter_valid_books(books, source_text=source)

        assert len(result) == 1
        assert result[0]["title"] == "The Hobbit"

    def test_validates_partial_title_match(self):
        """Should accept books where significant words appear in source."""
        books = [{"title": "The Lord of the Rings", "author": "Tolkien"}]
        source = "Lord of the Rings is a classic fantasy novel."

        result = _filter_valid_books(books, source_text=source)

        assert len(result) == 1

    def test_skips_short_words_in_validation(self):
        """Should only check words longer than 3 characters."""
        books = [{"title": "It", "author": "Stephen King"}]
        # "It" is too short to validate, so book passes
        source = "Some random text without the book title"

        result = _filter_valid_books(books, source_text=source)

        # Books with only short words in title skip validation
        assert len(result) == 1

    def test_handles_non_dict_entries(self):
        """Should skip non-dict entries in the list."""
        books = [
            {"title": "Valid Book", "author": "Author"},
            "not a dict",
            None,
            ["list", "item"],
        ]

        result = _filter_valid_books(books)

        assert len(result) == 1


class TestExtractIsbn:
    """Tests for _extract_isbn function."""

    def test_extracts_isbn_13(self):
        """Should prefer ISBN-13 over ISBN-10."""
        volume_info = {
            "industryIdentifiers": [
                {"type": "ISBN_10", "identifier": "1234567890"},
                {"type": "ISBN_13", "identifier": "9781234567890"},
            ]
        }

        result = _extract_isbn(volume_info)

        assert result == "9781234567890"

    def test_falls_back_to_isbn_10(self):
        """Should use ISBN-10 if ISBN-13 not available."""
        volume_info = {
            "industryIdentifiers": [
                {"type": "ISBN_10", "identifier": "1234567890"},
            ]
        }

        result = _extract_isbn(volume_info)

        assert result == "1234567890"

    def test_returns_none_when_no_isbn(self):
        """Should return None when no ISBN available."""
        volume_info = {"industryIdentifiers": []}

        result = _extract_isbn(volume_info)

        assert result is None

    def test_handles_missing_identifiers(self):
        """Should handle missing industryIdentifiers key."""
        volume_info = {}

        result = _extract_isbn(volume_info)

        assert result is None


class TestBuildAmazonUrl:
    """Tests for _build_amazon_url function."""

    def test_builds_search_url(self):
        """Should build Amazon search URL with title and author."""
        volume_info = {
            "title": "The Hobbit",
            "authors": ["J.R.R. Tolkien"],
        }

        result = _build_amazon_url(volume_info)

        assert "amazon.com/s?k=" in result
        assert "Hobbit" in result
        assert "Tolkien" in result

    def test_handles_missing_author(self):
        """Should build URL with just title if no author."""
        volume_info = {
            "title": "Anonymous Book",
            "authors": [],
        }

        result = _build_amazon_url(volume_info)

        assert "amazon.com/s?k=" in result
        assert "Anonymous" in result

    def test_returns_none_for_empty_title(self):
        """Should return None if title is empty."""
        volume_info = {"title": "", "authors": []}

        result = _build_amazon_url(volume_info)

        assert result is None
