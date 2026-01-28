"""Display formatting for books."""

import urllib.parse
from typing import Any

import click

from .models import Book, SearchResult


def format_book_result(result: SearchResult, rank: int, show_sources: bool = False) -> None:
    """Format and display a book search result."""
    book = result.book
    click.echo(f"{rank}. {book.title}")
    click.echo(f"   Author: {book.author or 'Unknown'}")

    if book.summary:
        click.echo(f"   {book.summary}")
    elif book.description:
        desc = book.description
        if len(desc) > 200:
            desc = desc[:200] + "..."
        click.echo(f"   {desc}")

    if show_sources and result.source_titles:
        for source_title in result.source_titles:
            click.echo(f"   Source: {source_title}")

    amazon_url = book.amazon_url
    if not amazon_url:
        search_query = f"{book.title} {book.author or ''}".strip()
        amazon_url = f"https://www.amazon.com/s?k={urllib.parse.quote(search_query)}"
    click.echo(f"   Amazon: {amazon_url}")

    click.echo(f"   Score: {result.score:.3f} | Status: {book.status}")
    click.echo()


def format_book_list_item(book: dict[str, Any] | Book) -> None:
    """Format and display a book in list view."""
    if isinstance(book, Book):
        book_id = book.id
        title = book.title
        author = book.author
        status = book.status
        isbn = book.isbn
    else:
        book_id = book["id"]
        title = book["title"]
        author = book.get("author")
        status = book.get("status", "new")
        isbn = book.get("isbn")

    click.echo(f"[{book_id}] {title}")
    click.echo(f"    Author: {author or 'Unknown'}")
    click.echo(f"    Status: {status}")
    if isbn:
        click.echo(f"    ISBN: {isbn}")
    click.echo()


def format_raw_result(
    rank: int,
    similarity: float,
    metadata: dict[str, Any],
) -> None:
    """Format and display a raw vector search result."""
    click.echo(f"{rank}. [{similarity:.3f}] {metadata.get('title', 'Unknown')}")
    click.echo(f"   Author: {metadata.get('author', 'Unknown')}")
    click.echo(f"   Source: {metadata.get('source_title', 'Unknown')}")
    click.echo()
