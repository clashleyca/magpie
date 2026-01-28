"""Book enrichment via Google Books API."""

import os
import time
from typing import Any

import requests

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY")

_api_quota_warned = False


class BookEnricher:
    """Enrich book metadata using Google Books API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or GOOGLE_BOOKS_API_KEY

    def enrich(self, title: str, author: str | None = None) -> dict[str, Any] | None:
        """Look up book metadata from Google Books API."""
        return lookup_google_books(title, author)


def lookup_google_books(title: str, author: str | None = None) -> dict[str, Any] | None:
    """Look up book metadata from Google Books API."""
    global _api_quota_warned

    # Rate limit to avoid hitting API quotas
    time.sleep(0.1)

    # Try with author first, then fall back to title-only if no results
    queries = [f'intitle:"{title}"']
    if author:
        queries.insert(0, f'intitle:"{title}" inauthor:"{author}"')

    for query in queries:
        result = _query_google_books(query)
        if result:
            return result
        time.sleep(0.1)  # Rate limit between retries

    return None


def _query_google_books(query: str) -> dict[str, Any] | None:
    """Execute a single Google Books API query."""
    global _api_quota_warned

    try:
        # Request multiple results to find best match (English, with description)
        params = {"q": query, "maxResults": 5, "langRestrict": "en"}
        if GOOGLE_BOOKS_API_KEY:
            params["key"] = GOOGLE_BOOKS_API_KEY
        response = requests.get(
            GOOGLE_BOOKS_API,
            params=params,
            timeout=10,
        )
        data = response.json()

        # Check for API errors (quota exceeded, disabled API, etc.)
        if "error" in data:
            if not _api_quota_warned:
                print(
                    f"\nWarning: Google Books API error - {data['error'].get('message', 'unknown error')}"
                )
                _api_quota_warned = True
            return None

        if data.get("totalItems", 0) > 0:
            # Find best result: prefer ones with longer descriptions
            best_item = None
            best_desc_len = 0
            for item in data.get("items", []):
                vol = item.get("volumeInfo", {})
                desc = vol.get("description", "")
                if len(desc) > best_desc_len:
                    best_desc_len = len(desc)
                    best_item = item

            # Fall back to first result if none have descriptions
            item = best_item or data["items"][0]
            volume_info = item.get("volumeInfo", {})
            return {
                "google_books_id": item.get("id"),
                "title": volume_info.get("title"),
                "authors": volume_info.get("authors", []),
                "description": volume_info.get("description"),
                "isbn": _extract_isbn(volume_info),
                "cover_url": volume_info.get("imageLinks", {}).get("thumbnail"),
                "amazon_url": _build_amazon_url(volume_info),
            }
    except requests.RequestException:
        pass

    return None


def _extract_isbn(volume_info: dict[str, Any]) -> str | None:
    """Extract ISBN-13 or ISBN-10 from volume info (prefers ISBN-13 for storage)."""
    identifiers = volume_info.get("industryIdentifiers", [])
    for id_type in ["ISBN_13", "ISBN_10"]:
        for identifier in identifiers:
            if identifier.get("type") == id_type:
                return identifier.get("identifier")
    return None


def _extract_isbn10(volume_info: dict[str, Any]) -> str | None:
    """Extract ISBN-10 specifically (needed for Amazon ASIN links)."""
    identifiers = volume_info.get("industryIdentifiers", [])
    for identifier in identifiers:
        if identifier.get("type") == "ISBN_10":
            return identifier.get("identifier")
    return None


def _build_amazon_url(volume_info: dict[str, Any]) -> str | None:
    """Build an Amazon URL for the book - direct link if ISBN-10 works, otherwise search."""
    title = volume_info.get("title", "")
    authors = volume_info.get("authors", [])

    # Try ISBN-10 direct link first (matches ASIN for books)
    isbn10 = _extract_isbn10(volume_info)
    if isbn10:
        direct_url = f"https://www.amazon.com/dp/{isbn10}"
        try:
            # Check if the URL works (HEAD request to avoid downloading full page)
            response = requests.head(direct_url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return direct_url
        except requests.RequestException:
            pass

    # Fall back to search URL
    if title:
        search_query = f"{title} {authors[0] if authors else ''}".strip()
        return f"https://www.amazon.com/s?k={requests.utils.quote(search_query)}"
    return None
