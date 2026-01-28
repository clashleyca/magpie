"""Tests for Reddit source adapter."""

import pytest

from magpie.sources.reddit import (
    extract_comment_texts,
    parse_reddit_json,
)


class TestParseRedditJson:
    """Tests for parse_reddit_json function."""

    def test_parses_valid_reddit_json(self):
        """Should extract post data and comments from Reddit JSON format."""
        data = [
            {
                "data": {
                    "children": [
                        {
                            "data": {
                                "id": "abc123",
                                "title": "Best books thread",
                                "selftext": "What are your favorites?",
                                "subreddit": "books",
                                "permalink": "/r/books/comments/abc123/best_books/",
                            }
                        }
                    ]
                }
            },
            {
                "data": {
                    "children": [
                        {
                            "kind": "t1",
                            "data": {
                                "id": "comment1",
                                "body": "I love The Hobbit by Tolkien",
                                "score": 100,
                            },
                        }
                    ]
                }
            },
        ]

        result = parse_reddit_json(data)

        assert result["id"] == "abc123"
        assert result["title"] == "Best books thread"
        assert result["selftext"] == "What are your favorites?"
        assert result["subreddit"] == "books"
        assert len(result["comments"]) == 1
        assert result["comments"][0]["body"] == "I love The Hobbit by Tolkien"

    def test_raises_on_invalid_format(self):
        """Should raise ValueError for invalid Reddit JSON."""
        with pytest.raises(ValueError, match="Invalid Reddit JSON format"):
            parse_reddit_json([])

        with pytest.raises(ValueError, match="Invalid Reddit JSON format"):
            parse_reddit_json({"not": "a list"})

    def test_flattens_nested_comments(self):
        """Should flatten nested comment replies."""
        data = [
            {"data": {"children": [{"data": {"id": "post1", "title": "Test"}}]}},
            {
                "data": {
                    "children": [
                        {
                            "kind": "t1",
                            "data": {
                                "id": "parent",
                                "body": "Parent comment",
                                "score": 50,
                                "replies": {
                                    "data": {
                                        "children": [
                                            {
                                                "kind": "t1",
                                                "data": {
                                                    "id": "child",
                                                    "body": "Child reply",
                                                    "score": 10,
                                                },
                                            }
                                        ]
                                    }
                                },
                            },
                        }
                    ]
                }
            },
        ]

        result = parse_reddit_json(data)

        assert len(result["comments"]) == 2
        assert result["comments"][0]["id"] == "parent"
        assert result["comments"][0]["depth"] == 0
        assert result["comments"][1]["id"] == "child"
        assert result["comments"][1]["depth"] == 1


class TestExtractCommentTexts:
    """Tests for extract_comment_texts function."""

    def test_extracts_all_comment_bodies(self):
        """Should extract body text from all comments."""
        thread = {
            "selftext": "",
            "comments": [
                {"body": "First comment"},
                {"body": "Second comment"},
            ],
        }

        result = extract_comment_texts(thread)

        assert result == ["First comment", "Second comment"]

    def test_includes_selftext_if_present(self):
        """Should include post body (selftext) if present."""
        thread = {
            "selftext": "Post body text",
            "comments": [{"body": "A comment"}],
        }

        result = extract_comment_texts(thread)

        assert result == ["Post body text", "A comment"]

    def test_filters_deleted_and_removed(self):
        """Should skip [deleted] and [removed] comments."""
        thread = {
            "selftext": "",
            "comments": [
                {"body": "Good comment"},
                {"body": "[deleted]"},
                {"body": "[removed]"},
                {"body": "Another good one"},
            ],
        }

        result = extract_comment_texts(thread)

        assert result == ["Good comment", "Another good one"]

    def test_filters_empty_comments(self):
        """Should skip empty or whitespace-only comments."""
        thread = {
            "selftext": "",
            "comments": [
                {"body": "Real comment"},
                {"body": ""},
                {"body": "   "},
            ],
        }

        result = extract_comment_texts(thread)

        assert result == ["Real comment"]
