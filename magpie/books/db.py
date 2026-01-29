"""Database operations for books."""

import json
import sqlite3


def _init_tables(conn: sqlite3.Connection) -> None:
    """Initialize database tables."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            description TEXT,
            summary TEXT,
            google_books_id TEXT,
            isbn TEXT,
            cover_url TEXT,
            amazon_url TEXT,
            status TEXT DEFAULT 'new',
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT DEFAULT 'reddit',
            external_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS book_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            source_id INTEGER NOT NULL,
            context_id TEXT,
            score INTEGER DEFAULT 0,
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (source_id) REFERENCES sources(id),
            UNIQUE(book_id, source_id, context_id)
        );

        CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
        CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
    """)
    _migrate_tables(conn)
    conn.commit()


def _migrate_tables(conn: sqlite3.Connection) -> None:
    """Migrate old table names to new names if needed."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents'"
    )
    if cursor.fetchone():
        conn.executescript("""
            INSERT OR IGNORE INTO books (id, title, author, description, summary, google_books_id, isbn, cover_url, amazon_url, status, metadata, created_at, updated_at)
            SELECT id, title, author, description, summary, external_id, isbn, cover_url, external_url, status, metadata, created_at, updated_at
            FROM documents;

            DROP TABLE IF EXISTS documents;
        """)

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='document_sources'"
    )
    if cursor.fetchone():
        conn.executescript("""
            INSERT OR IGNORE INTO book_sources (id, book_id, source_id, context_id, score)
            SELECT id, document_id, source_id, context_id, score
            FROM document_sources;

            DROP TABLE IF EXISTS document_sources;
        """)


def ensure_tables(conn: sqlite3.Connection) -> None:
    """Ensure tables exist (call on first use)."""
    _init_tables(conn)


def add_book(
    conn: sqlite3.Connection,
    title: str,
    author: str | None = None,
    description: str | None = None,
    summary: str | None = None,
    google_books_id: str | None = None,
    isbn: str | None = None,
    cover_url: str | None = None,
    amazon_url: str | None = None,
    metadata: dict | None = None,
) -> int:
    """Add a book to the database, returning its ID."""
    ensure_tables(conn)
    metadata_json = json.dumps(metadata) if metadata else None
    cursor = conn.execute(
        """
        INSERT INTO books (title, author, description, summary, google_books_id, isbn, cover_url, amazon_url, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            author,
            description,
            summary,
            google_books_id,
            isbn,
            cover_url,
            amazon_url,
            metadata_json,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_book(conn: sqlite3.Connection, book_id: int) -> sqlite3.Row | None:
    """Get a book by ID."""
    ensure_tables(conn)
    return conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()


def list_books(
    conn: sqlite3.Connection,
    status: str | None = None,
) -> list[sqlite3.Row]:
    """List all books, optionally filtered by status."""
    ensure_tables(conn)
    query = "SELECT * FROM books"
    params = []

    if status:
        query += " WHERE status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC"

    return conn.execute(query, params).fetchall()


def update_status(conn: sqlite3.Connection, book_id: int, status: str) -> bool:
    """Update a book's status."""
    ensure_tables(conn)
    cursor = conn.execute(
        "UPDATE books SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, book_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def find_book_by_title_author(
    conn: sqlite3.Connection,
    title: str,
    author: str | None = None,
) -> sqlite3.Row | None:
    """Find an existing book by title and author (case-insensitive)."""
    ensure_tables(conn)
    if author:
        return conn.execute(
            "SELECT * FROM books WHERE LOWER(title) = LOWER(?) AND LOWER(author) = LOWER(?)",
            (title, author),
        ).fetchone()
    return conn.execute(
        "SELECT * FROM books WHERE LOWER(title) = LOWER(?)",
        (title,),
    ).fetchone()


def find_book_by_google_id(
    conn: sqlite3.Connection,
    google_books_id: str,
) -> sqlite3.Row | None:
    """Find an existing book by Google Books ID."""
    ensure_tables(conn)
    return conn.execute(
        "SELECT * FROM books WHERE google_books_id = ?",
        (google_books_id,),
    ).fetchone()


def delete_book(conn: sqlite3.Connection, book_id: int) -> bool:
    """Delete a book from the database."""
    ensure_tables(conn)
    cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    return cursor.rowcount > 0


def add_source(
    conn: sqlite3.Connection,
    external_id: str,
    title: str,
    source_type: str = "reddit",
    url: str | None = None,
    metadata: dict | None = None,
) -> int:
    """Add a source to the database, returning its ID. Returns existing ID if already present."""
    ensure_tables(conn)
    existing = conn.execute(
        "SELECT id FROM sources WHERE external_id = ?", (external_id,)
    ).fetchone()
    if existing:
        return existing["id"]

    metadata_json = json.dumps(metadata) if metadata else None
    cursor = conn.execute(
        "INSERT INTO sources (source_type, external_id, title, url, metadata) VALUES (?, ?, ?, ?, ?)",
        (source_type, external_id, title, url, metadata_json),
    )
    conn.commit()
    return cursor.lastrowid


def get_source(conn: sqlite3.Connection, source_id: int) -> sqlite3.Row | None:
    """Get a source by ID."""
    ensure_tables(conn)
    return conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()


def get_source_by_external_id(
    conn: sqlite3.Connection, external_id: str
) -> sqlite3.Row | None:
    """Get a source by its external ID."""
    ensure_tables(conn)
    return conn.execute(
        "SELECT * FROM sources WHERE external_id = ?", (external_id,)
    ).fetchone()


def list_sources(
    conn: sqlite3.Connection, source_type: str | None = None
) -> list[sqlite3.Row]:
    """List all sources, optionally filtered by type."""
    ensure_tables(conn)
    if source_type:
        return conn.execute(
            "SELECT * FROM sources WHERE source_type = ? ORDER BY created_at DESC",
            (source_type,),
        ).fetchall()
    return conn.execute("SELECT * FROM sources ORDER BY created_at DESC").fetchall()


def delete_source(conn: sqlite3.Connection, source_id: int) -> bool:
    """Delete a source from the database."""
    ensure_tables(conn)
    cursor = conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    conn.commit()
    return cursor.rowcount > 0


def add_book_source(
    conn: sqlite3.Connection,
    book_id: int,
    source_id: int,
    context_id: str | None = None,
    score: int = 0,
) -> None:
    """Record that a book was mentioned in a source."""
    ensure_tables(conn)
    # Check if already exists (NULL != NULL in SQL unique constraints)
    existing = conn.execute(
        "SELECT 1 FROM book_sources WHERE book_id = ? AND source_id = ?",
        (book_id, source_id),
    ).fetchone()
    if existing:
        return
    conn.execute(
        """
        INSERT INTO book_sources (book_id, source_id, context_id, score)
        VALUES (?, ?, ?, ?)
        """,
        (book_id, source_id, context_id, score),
    )
    conn.commit()


def get_book_sources(conn: sqlite3.Connection, book_id: int) -> list[sqlite3.Row]:
    """Get all sources where a book was mentioned."""
    ensure_tables(conn)
    return conn.execute(
        """
        SELECT s.* FROM sources s
        JOIN book_sources bs ON s.id = bs.source_id
        WHERE bs.book_id = ?
        """,
        (book_id,),
    ).fetchall()


def get_books_for_source(conn: sqlite3.Connection, source_id: int) -> list[sqlite3.Row]:
    """Get all books mentioned in a source."""
    ensure_tables(conn)
    return conn.execute(
        """
        SELECT b.* FROM books b
        JOIN book_sources bs ON b.id = bs.book_id
        WHERE bs.source_id = ?
        """,
        (source_id,),
    ).fetchall()


def get_book_source_count(conn: sqlite3.Connection, book_id: int) -> int:
    """Get the number of sources a book is mentioned in."""
    ensure_tables(conn)
    result = conn.execute(
        "SELECT COUNT(DISTINCT source_id) FROM book_sources WHERE book_id = ?",
        (book_id,),
    ).fetchone()
    return result[0] if result else 0


def delete_book_sources_for_source(conn: sqlite3.Connection, source_id: int) -> int:
    """Delete all book mentions for a source. Returns count deleted."""
    ensure_tables(conn)
    cursor = conn.execute(
        "DELETE FROM book_sources WHERE source_id = ?",
        (source_id,),
    )
    conn.commit()
    return cursor.rowcount
