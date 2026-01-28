# Magpie

A book finder for Reddit recommendation threads. Extracts books from threads like "What's the best novel you've read?" and makes them searchable.

## What It Does

1. **Extracts books** from Reddit threads using LLM
2. **Enriches metadata** via Google Books API (descriptions, covers, ISBNs, Amazon links)
3. **Enables semantic search** - find "obscure sci-fi about AI" without exact keywords
4. **Deduplicates** across sources and tracks where each book was mentioned

## Quick Start

```bash
# Add a Reddit thread
magpie add "https://reddit.com/r/books/comments/..."

# Search for books
magpie search "obscure historical fiction"

# List all indexed books
magpie list
```

## Project Structure
```
magpie/
├── core/                 # Infrastructure (connections only)
│   ├── sqlite.py         # SQLite connection
│   └── chroma.py         # ChromaDB connection
├── books/                # All book logic
│   ├── models.py         # Book, Source, SearchResult
│   ├── db.py             # Database operations
│   ├── vector.py         # Vector store operations
│   ├── search.py         # Search orchestration
│   ├── encoder.py        # Embeddings + text processing
│   ├── extractor.py      # LLM book extraction
│   ├── enricher.py       # Google Books API
│   └── display.py        # CLI formatting
├── sources/              # Input source adapters
│   └── reddit.py         # Reddit fetcher + parser
├── cli/                  # CLI interface
│   └── commands.py
└── tests/
data/
├── magpie.db             # SQLite database
├── chroma/               # Vector storage
└── sources/              # Cached source JSON
```

## Setup

### Requirements

- Python 3.12+
- Ollama (for book extraction)

### Installation
```bash
git clone <repo-url>
cd magpie

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .

# Install Ollama and pull model
brew install ollama
ollama serve  # Run in separate terminal
ollama pull llama3.2
```

## Usage

### Adding Sources
```bash
magpie add "https://reddit.com/r/books/comments/xyz/best_novels"
magpie add saved_thread.json
magpie add --force "https://reddit.com/..."  # Re-process
magpie add -v "https://reddit.com/..."       # Verbose
```

### Searching
```bash
magpie search "ancient greece"
magpie search "sci-fi" --limit 5
magpie search "memoirs" --raw
```

### Managing Books
```bash
magpie list
magpie list --status reading
magpie status <book_id> reading
```

### Managing Sources
```bash
magpie sources
magpie remove-source <source_id>
```

## How It Works

### Extraction Flow

1. Parse Reddit thread JSON
2. For each comment: extract books via Ollama, validate, enrich via Google Books
3. Store in SQLite, create vector embeddings in ChromaDB

### Search Flow

1. Encode query with sentence-transformers
2. Find similar book chunks via ChromaDB
3. Fetch full details from SQLite, display with Amazon links

## Design Decisions

- **Book-centric chunks**: Book descriptions from Google Books provide better semantic content than Reddit comments
- **Source titles in chunks**: Adds searchable context like "obscure", "underrated"
- **ChromaDB**: Local-first, no API costs
- **bge-small embeddings**: Fast, runs locally

## License

MIT
