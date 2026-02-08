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
        console.print(f"   ID: {book.id} | Score: {result.score:.3f} | Status: {book.status}")

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


def format_book_detail(book: Book, sources: list[dict[str, Any]] | None = None) -> None:
    """Format and display detailed book information."""
    title = escape(book.title)
    author = escape(book.author or "Unknown")

    console.print(f"[bold]{title}[/bold]")
    console.print(f"by {author}")
    console.print()

    # Status
    console.print(f"[dim]ID:[/dim] {book.id}  [dim]Status:[/dim] {book.status}")

    # ISBN
    if book.isbn:
        console.print(f"[dim]ISBN:[/dim] {book.isbn}")

    console.print()

    # Summary (LLM-generated)
    if book.summary:
        console.print("[dim]Summary:[/dim]")
        console.print(escape(book.summary))
        console.print()

    # Description (Google Books)
    if book.description:
        console.print("[dim]Google Books:[/dim]")
        console.print(escape(book.description))
        console.print()

    # Links
    if book.amazon_url:
        console.print(f"[dim]Amazon:[/dim] {book.amazon_url}")
    if book.cover_url:
        console.print(f"[dim]Cover:[/dim] {book.cover_url}")

    # Sources
    if sources:
        console.print()
        console.print(f"[dim]Found in {len(sources)} source(s):[/dim]")
        for src in sources:
            url = src["url"] or f"https://reddit.com/comments/{src['external_id'] or ''}"
            src_title = escape(src["title"][:60] + "..." if len(src["title"]) > 60 else src["title"])
            console.print(f"  • {src_title}")
            console.print(f"    {url}")

    # Timestamps
    if book.created_at or book.updated_at:
        console.print()
        if book.created_at:
            console.print(f"[dim]Added:[/dim] {book.created_at}")
        if book.updated_at and book.updated_at != book.created_at:
            console.print(f"[dim]Updated:[/dim] {book.updated_at}")
