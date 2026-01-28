"""Reddit source adapter for fetching and parsing threads."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import requests

# Reddit's public JSON endpoint (no auth required, rate limited)
REDDIT_JSON_SUFFIX = ".json"


class RedditAdapter:
    """Adapter for fetching Reddit threads."""

    def __init__(self, user_agent: str = "Magpie/1.0 (content recommendation tracker)"):
        self.user_agent = user_agent

    def fetch(self, url: str) -> dict[str, Any] | None:
        """Fetch a Reddit thread from URL."""
        raw_data = fetch_thread_json(url, user_agent=self.user_agent)
        if raw_data:
            return parse_reddit_json(raw_data)
        return None

    def extract_texts(self, content: dict[str, Any]) -> list[str]:
        """Extract comment texts from a parsed thread."""
        return extract_comment_texts(content)


def fetch_thread_json(
    url: str, user_agent: str = "Magpie/1.0"
) -> list[dict[str, Any]] | None:
    """Fetch a Reddit thread as JSON.

    Appends .json to the URL and fetches the public JSON representation.
    Rate limited but doesn't require API credentials.
    """
    # Normalize URL
    if "?" in url:
        # Handle URLs with query params
        base, params = url.split("?", 1)
        if not base.endswith(REDDIT_JSON_SUFFIX):
            url = base.rstrip("/") + REDDIT_JSON_SUFFIX + "?" + params
    elif not url.endswith(REDDIT_JSON_SUFFIX):
        url = url.rstrip("/") + REDDIT_JSON_SUFFIX

    try:
        response = requests.get(
            url,
            headers={"User-Agent": user_agent},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching thread: {e}")
        return None


def load_thread_json(source: str) -> dict[str, Any] | list[Any]:
    """Load thread data from a file path or raw JSON string."""
    path = Path(source)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return json.loads(source)


def parse_reddit_json(data: list[Any]) -> dict[str, Any]:
    """Parse Reddit's JSON format into a cleaner structure.

    Reddit returns a list with two elements:
    - [0]: The submission/post
    - [1]: The comments tree
    """
    if not isinstance(data, list) or len(data) < 2:
        raise ValueError("Invalid Reddit JSON format")

    post_data = data[0]["data"]["children"][0]["data"]
    comments_data = data[1]["data"]["children"]

    return {
        "id": post_data.get("id"),
        "title": post_data.get("title"),
        "selftext": post_data.get("selftext", ""),
        "subreddit": post_data.get("subreddit"),
        "url": f"https://reddit.com{post_data.get('permalink', '')}",
        "comments": list(_flatten_comments(comments_data)),
    }


def _flatten_comments(
    comments: list[dict[str, Any]], depth: int = 0
) -> Iterator[dict[str, Any]]:
    """Recursively flatten the comment tree."""
    for item in comments:
        if item.get("kind") != "t1":
            continue

        comment = item.get("data", {})
        yield {
            "id": comment.get("id"),
            "body": comment.get("body", ""),
            "score": comment.get("score", 0),
            "depth": depth,
        }

        # Recurse into replies
        replies = comment.get("replies")
        if isinstance(replies, dict):
            reply_children = replies.get("data", {}).get("children", [])
            yield from _flatten_comments(reply_children, depth + 1)


def extract_comment_texts(thread: dict[str, Any]) -> list[str]:
    """Extract all comment bodies from a parsed thread."""
    texts = []

    # Include post body if present
    if thread.get("selftext"):
        texts.append(thread["selftext"])

    # Include all comments
    for comment in thread.get("comments", []):
        body = comment.get("body", "").strip()
        if body and body != "[deleted]" and body != "[removed]":
            texts.append(body)

    return texts
