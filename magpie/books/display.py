"""Display formatting for books."""

import urllib.parse
from typing import Any

from rich.console import Console
from rich.markup import escape

from .models import Book, SearchResult

console = Console()


def format_book_result(
    result: SearchResult,
    rank: int,
    sources: list[dict[str, Any]] | None = None,
    verbose: bool = False,
) -> None:
    """Format and display a book search result."""
    book = result.book

    # Line 1: rank, title, author
    title = escape(book.title)
    author = escape(book.author or "Unknown")
    console.print(f"{rank}. [bold]{title}[/bold] — {author}")

    # Line 2: description/summary (first sentence only)
    desc = book.summary or book.description or ""
    # Take first sentence only
    if ". " in desc:
        desc = desc.split(". ")[0] + "."
    if desc:
        console.print(f"   {escape(desc)}")

    # Reddit links (verbose only)
    if verbose and sources:
        for src in sources:
            url = src["url"] or f"https://reddit.com/comments/{src['external_id'] or ''}"
            console.print(f"   Reddit: {url}")

    # Amazon link
    amazon_url = book.amazon_url
    if not amazon_url:
        search_query = f"{book.title} {book.author or ''}".strip()
        amazon_url = f"https://www.amazon.com/s?k={urllib.parse.quote(search_query)}"
    console.print(f"   Amazon: {amazon_url}")

    # Score and status (verbose only)
    if verbose:
        console.print(f"   Score: {result.score:.3f} | Status: {book.status}")

    console.print()


def format_book_list_item(book: dict[str, Any] | Book) -> None:
    """Format and display a book in list view."""
    if isinstance(book, Book):
        book_id = book.id
        title = book.title
        author = book.author
        status = book.status
    else:
        book_id = book["id"]
        title = book["title"]
        author = book["author"]
        status = book["status"] or "new"

    title = escape(title)
    author = escape(author or "Unknown")
    console.print(
        f"[dim]{book_id}.[/dim] [bold]{title}[/bold] — {author}  [dim]({status})[/dim]"
    )


def format_raw_result(
    rank: int,
    similarity: float,
    metadata: dict[str, Any],
) -> None:
    """Format and display a raw vector search result."""
    title = escape(metadata.get("title", "Unknown"))
    author = escape(metadata.get("author", "Unknown"))
    source = escape(metadata.get("source_title", "Unknown"))
    console.print(
        f"{rank}. [bold]{title}[/bold] — {author}  [dim][{similarity:.3f}][/dim]"
    )
    console.print(f"   Source: {source}")
    console.print()
