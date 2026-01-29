"""Click CLI interface for magpie."""

import json
from pathlib import Path

import click

from ..books import BookEnricher, BookExtractor, QuotaExceededError, db, encoder, vector
from ..books.display import format_book_list_item, format_book_result, format_raw_result
from ..books.models import Book, SearchResult
from ..core.chroma import get_client, get_collection
from ..core.sqlite import get_connection
from ..sources import reddit

DATA_DIR = Path(__file__).parent.parent.parent / "data"
SOURCES_DIR = DATA_DIR / "sources"


@click.group()
def cli():
    """Magpie - Semantic search for book recommendations."""
    pass


@cli.command()
@click.argument("source")
@click.option("--model", default="llama3.2", help="Ollama model for book extraction")
@click.option("--force", is_flag=True, help="Re-process source even if already indexed")
@click.option("--verbose", "-v", is_flag=True, help="Show extraction details")
def add(source, model, force, verbose):
    """Add a Reddit thread from URL or JSON file."""
    click.echo(f"Adding source from: {source}")

    conn = get_connection()
    db.ensure_tables(conn)
    reddit_id = _extract_reddit_id(source)

    if reddit_id and not force:
        existing = db.get_source_by_external_id(conn, reddit_id)
        if existing:
            click.echo(
                f"Source already indexed (id={existing['id']}). Use --force to re-process."
            )
            return

    thread_data = _load_thread(source, reddit_id)
    if not thread_data:
        click.echo("Failed to load source data.", err=True)
        return

    click.echo(f"Thread: {thread_data['title']}")
    click.echo(f"Subreddit: r/{thread_data.get('subreddit', 'unknown')}")
    click.echo(f"Comments: {len(thread_data.get('comments', []))}")

    # Test Google Books API before processing
    enricher = BookEnricher()
    try:
        enricher.test_api()
    except QuotaExceededError:
        click.echo("\nGoogle Books rate limit reached (HTTP 429).", err=True)
        click.echo(
            "You can wait for the limit to reset, or set a Google Books API key to use your own quota.",
            err=True,
        )
        click.echo("(Set GOOGLE_BOOKS_API_KEY to avoid shared limits.)", err=True)
        return

    source_id = db.add_source(
        conn,
        external_id=thread_data["id"],
        title=thread_data["title"],
        source_type="reddit",
        url=thread_data.get("url"),
        metadata={"subreddit": thread_data.get("subreddit")},
    )

    comment_texts = reddit.extract_comment_texts(thread_data)
    click.echo(f"\nExtracting books from {len(comment_texts)} comments...")

    extractor = BookExtractor(model=model)

    books_found = []
    if verbose:
        for i, text in enumerate(comment_texts):
            extracted = extractor.extract(text)
            if extracted:
                click.echo(
                    f"[{i + 1}/{len(comment_texts)}] Found: {[b.get('title') for b in extracted]}"
                )
            for book in extracted:
                books_found.append((book, text))
    else:
        with click.progressbar(comment_texts, label="Processing comments") as comments:
            for text in comments:
                extracted = extractor.extract(text)
                for book in extracted:
                    books_found.append((book, text))

    click.echo(f"Found {len(books_found)} book mentions")

    click.echo("\nEnriching with Google Books API...")
    books_added = 0
    books_skipped = 0

    chroma_client = get_client()
    collection = get_collection(chroma_client)

    for book_info, _comment_text in books_found:
        title = (book_info.get("title") or "").strip()
        author = (book_info.get("author") or "").strip()

        if not title:
            continue

        existing = db.find_book_by_title_author(conn, title, author)
        if existing:
            db.add_book_source(conn, existing["id"], source_id)
            books_skipped += 1
            continue

        try:
            google_data = enricher.enrich(title, author)
        except QuotaExceededError:
            click.echo("\nGoogle Books rate limit reached (HTTP 429).", err=True)
            click.echo(
                "You can wait for the limit to reset, or set a Google Books API key to use your own quota.",
                err=True,
            )
            click.echo("(Set GOOGLE_BOOKS_API_KEY to avoid shared limits.)", err=True)
            click.echo(f"\nProgress: {books_added} added, {books_skipped} skipped.")
            return

        if google_data:
            # Check for duplicate by Google Books ID
            google_id = google_data.get("google_books_id")
            if google_id:
                existing = db.find_book_by_google_id(conn, google_id)
                if existing:
                    db.add_book_source(conn, existing["id"], source_id)
                    books_skipped += 1
                    continue

            description = google_data.get("description", "")
            summary = extractor.summarize(description) if description else None
            book_id = db.add_book(
                conn,
                title=google_data.get("title") or title,
                author=", ".join(google_data.get("authors", [])) or author,
                description=description,
                summary=summary,
                google_books_id=google_data.get("google_books_id"),
                isbn=google_data.get("isbn"),
                cover_url=google_data.get("cover_url"),
                amazon_url=google_data.get("amazon_url"),
            )
            final_author = ", ".join(google_data.get("authors", [])) or author
            final_title = google_data.get("title") or title
        else:
            book_id = db.add_book(conn, title=title, author=author)
            description = ""
            final_author = author
            final_title = title

        db.add_book_source(conn, book_id, source_id)

        if description:
            chunk_text = encoder.build_book_chunk(
                title=final_title,
                author=final_author or "Unknown",
                description=description,
                source_titles=[thread_data["title"]],
            )
            embedding = encoder.encode(chunk_text)
            vector.add_book_chunk(
                collection,
                book_id=book_id,
                text=chunk_text,
                embedding=embedding,
                metadata={
                    "title": final_title,
                    "author": final_author or "Unknown",
                    "source_title": thread_data["title"],
                },
            )
            books_added += 1
            click.echo(f"  + {final_title} by {final_author or 'Unknown'}")
        else:
            books_skipped += 1
            click.echo(f"  ~ {final_title} (no description, stored but not searchable)")

    click.echo(
        f"\nDone! Added {books_added} new books, {books_skipped} already indexed."
    )


def _extract_reddit_id(source: str) -> str | None:
    """Extract Reddit thread ID from URL or filename."""
    import re

    match = re.search(r"/comments/([a-zA-Z0-9]+)", source)
    if match:
        return match.group(1)
    if source.endswith(".json"):
        name = Path(source).stem
        if re.match(r"^[a-zA-Z0-9]+$", name):
            return name
    return None


def _load_thread(source: str, reddit_id: str | None = None) -> dict | None:
    """Load thread data from cache, file, or URL."""
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    if Path(source).exists():
        try:
            raw_data = reddit.load_thread_json(source)
            if isinstance(raw_data, list):
                return reddit.parse_reddit_json(raw_data)
            return raw_data
        except Exception as e:
            click.echo(f"Error parsing file: {e}", err=True)
            return None

    if reddit_id:
        cache_file = SOURCES_DIR / f"{reddit_id}.json"
        if cache_file.exists():
            click.echo(f"Loading from cache: {cache_file}")
            try:
                raw_data = reddit.load_thread_json(str(cache_file))
                if isinstance(raw_data, list):
                    return reddit.parse_reddit_json(raw_data)
                return raw_data
            except Exception as e:
                click.echo(f"Error reading cache: {e}", err=True)

    if "reddit.com" in source or "redd.it" in source:
        click.echo("Fetching from Reddit...")
        raw_data = reddit.fetch_thread_json(source)
        if raw_data:
            if reddit_id:
                cache_file = SOURCES_DIR / f"{reddit_id}.json"
                with open(cache_file, "w") as f:
                    json.dump(raw_data, f, indent=2)
                click.echo(f"Saved to cache: {cache_file}")
            return reddit.parse_reddit_json(raw_data)

    click.echo(
        "Could not load source. Provide a valid Reddit URL or JSON file.", err=True
    )
    return None


@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=5, help="Number of results to return")
@click.option("--raw", is_flag=True, help="Show raw vector search results")
@click.option("--verbose", "-v", is_flag=True, help="Show source threads")
@click.option("--new", "new_only", is_flag=True, help="Only show books not yet viewed")
def search(query, limit, raw, verbose, new_only):
    """Search for books by semantic query."""
    query_embedding = encoder.encode(query)

    chroma_client = get_client()
    collection = get_collection(chroma_client)

    # Fetch extra results to account for deleted/filtered books
    fetch_limit = limit * 3
    results = vector.search(collection, query_embedding, n_results=fetch_limit)

    if not results["ids"] or not results["ids"][0]:
        click.echo("No books found. Try adding some sources first.")
        return

    if raw:
        click.echo(f"\nRaw results for: {query}\n")
        raw_items = list(
            zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
                strict=False,
            )
        )
        num_raw = len(raw_items)
        for i, (_doc_id, _document, metadata, distance) in enumerate(
            reversed(raw_items)
        ):
            similarity = 1 - distance
            rank = num_raw - i
            format_raw_result(rank, similarity, metadata)
        return

    conn = get_connection()
    db.ensure_tables(conn)
    click.echo(f"\nResults for: {query}\n")

    result_items = list(
        zip(
            results["ids"][0],
            results["metadatas"][0],
            results["distances"][0],
            strict=False,
        )
    )

    # Collect books to display
    displayed_books = []
    for _doc_id, metadata, distance in reversed(result_items):
        if len(displayed_books) >= limit:
            break

        book_id = metadata.get("book_id") or metadata.get("document_id")
        row = db.get_book(conn, book_id) if book_id else None

        if row:
            book = Book.from_row(row)
            # Skip deleted books
            if book.status == "deleted":
                continue
            # Skip if filtering by new and book has been viewed
            if new_only and book.status != "new":
                continue
            sources = db.get_book_sources(conn, book_id)
            displayed_books.append((book, sources, 1 - distance))

    if not displayed_books:
        if new_only:
            click.echo("No new books found. Try without --new to see viewed books.")
        else:
            click.echo("No matching books found.")
        return

    # Display results (reversed so best match is #1 at bottom)
    num_results = len(displayed_books)
    for i, (book, sources, score) in enumerate(displayed_books):
        result = SearchResult(book=book, score=score, source_titles=[])
        rank = num_results - i
        format_book_result(result, rank, sources, verbose=verbose)

        # Mark as viewed if currently new
        if book.status == "new":
            db.update_status(conn, book.id, "viewed")


@cli.command("list")
@click.option(
    "--status",
    "filter_status",
    help="Filter by status (new, interested, reading, finished)",
)
@click.option("--filter", "-f", "filter_text", help="Filter by title or author (case-insensitive)")
@click.option("--limit", "-n", default=50, help="Number of books to show")
def list_books(filter_status, filter_text, limit):
    """List all indexed books."""
    conn = get_connection()
    db.ensure_tables(conn)
    books = db.list_books(conn, status=filter_status)

    if filter_text:
        filter_lower = filter_text.lower()
        books = [
            b for b in books
            if filter_lower in (b["title"] or "").lower()
            or filter_lower in (b["author"] or "").lower()
        ]

    if not books:
        if filter_status or filter_text:
            click.echo("No books match the filter.")
        else:
            click.echo("No books indexed yet. Use 'magpie add' to add a source.")
        return

    total = len(books)
    books = books[:limit]
    if filter_status or filter_text:
        click.echo(f"Matching books: {total}")
    else:
        click.echo(f"Total books: {total}")
    click.echo()

    for book in books:
        format_book_list_item(book)

    if total > limit:
        click.echo(f"... and {total - limit} more. Use --limit to show more.")


VALID_STATUSES = ["new", "viewed", "interested", "reading", "finished", "dropped", "deleted"]


@cli.command()
@click.argument("book_id", type=int)
@click.argument("new_status", required=False)
def status(book_id, new_status):
    """Update a book's reading status."""
    if new_status is None:
        click.echo(f"Valid statuses: {', '.join(VALID_STATUSES)}")
        return

    if new_status not in VALID_STATUSES:
        click.echo(
            f"Invalid status '{new_status}'. Valid options: {', '.join(VALID_STATUSES)}",
            err=True,
        )
        return

    conn = get_connection()
    db.ensure_tables(conn)
    book = db.get_book(conn, book_id)

    if not book:
        click.echo(f"Book {book_id} not found.", err=True)
        return

    old_status = book["status"]
    if old_status == new_status:
        click.echo(f"Book already has status '{new_status}'.")
        return

    db.update_status(conn, book_id, new_status)
    click.echo(f"Updated '{book['title']}': {old_status} -> {new_status}")


@cli.command("sources")
def list_sources():
    """List all indexed sources."""
    conn = get_connection()
    db.ensure_tables(conn)
    sources = db.list_sources(conn)

    if not sources:
        click.echo("No sources indexed yet.")
        return

    click.echo(f"{'ID':<4} {'External ID':<12} {'Title':<50} {'Books':<6}")
    click.echo("-" * 75)

    for src in sources:
        books = db.get_books_for_source(conn, src["id"])
        title = src["title"][:47] + "..." if len(src["title"]) > 50 else src["title"]
        click.echo(
            f"{src['id']:<4} {src['external_id']:<12} {title:<50} {len(books):<6}"
        )
        if src["url"]:
            click.echo(f"     {src['url']}")


@cli.command("remove-source")
@click.argument("source_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def remove_source(source_id, yes):
    """Remove a source and its books (keeps books shared with other sources)."""
    conn = get_connection()
    db.ensure_tables(conn)

    source = db.get_source(conn, source_id)
    if not source:
        click.echo(f"Source {source_id} not found.", err=True)
        return

    books = db.get_books_for_source(conn, source_id)
    books_to_delete = []
    books_to_keep = []

    for book in books:
        mention_count = db.get_book_source_count(conn, book["id"])
        if mention_count <= 1:
            books_to_delete.append(book)
        else:
            books_to_keep.append(book)

    click.echo(f"Source: {source['title']}")
    click.echo(f"  Books to DELETE (only in this source): {len(books_to_delete)}")
    click.echo(f"  Books to KEEP (in other sources): {len(books_to_keep)}")

    if books_to_delete:
        click.echo("\nBooks that will be deleted:")
        for book in books_to_delete[:10]:
            click.echo(f"  - {book['title']} by {book['author'] or 'Unknown'}")
        if len(books_to_delete) > 10:
            click.echo(f"  ... and {len(books_to_delete) - 10} more")

    if not yes and not click.confirm("\nProceed?"):
        click.echo("Cancelled.")
        return

    db.delete_book_sources_for_source(conn, source_id)

    chroma_client = get_client()
    collection = get_collection(chroma_client)

    for book in books_to_delete:
        db.delete_book(conn, book["id"])
        vector.delete_book(collection, book["id"])

    db.delete_source(conn, source_id)

    click.echo(f"\nRemoved source and {len(books_to_delete)} books.")


if __name__ == "__main__":
    cli()
