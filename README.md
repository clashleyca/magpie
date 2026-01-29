# Magpie

<img src="assets/magpie.png" alt="Magpie" width="200">

Search the book recommendations you already trust.

---

## Why I Wrote This (and Why It’s Different)

I have years of saved Reddit threads full of book recommendations — *“books I’ve never heard of,” “overlooked favorites,” “the best novel you’ve read,”* and so on.  
They’re great recommendations… and I almost never remember to look at them when I’m actually trying to find something to read.

I also wanted recommendations that *weren’t* dominated by bestsellers or publisher-driven promotion. Many book recommendation systems surface the same popular titles. In contrast, Reddit recommendation threads — especially ones focused on “overlooked” or “never read” books — are full of thoughtful suggestions from real people, often for books that don’t show up in Amazon, Goodreads, Google, or chatbot recommendations.

**Magpie lets me load those saved Reddit threads and then search *only that pile* of recommendations using natural, vibe-based prompts.**  
Instead of starting from scratch, I’m searching a set of recommendations I already trust.

Magpie works best for broad, taste-based queries (e.g. *“hopeful but not grimdark dystopia”*), not ultra-specific plot details.

**In short:** Magpie is semantic search over your saved Reddit recommendation threads (plus Google Books blurbs), not a general book recommender.

---

## What It Does

Magpie:

1. **Extracts books** from Reddit recommendation threads using an LLM  
2. **Enriches metadata** via Google Books (descriptions, ISBNs, Amazon links)  
3. **Enables semantic search** over those recommendations (not the whole internet)  
4. **Deduplicates books** across threads and tracks where each one was mentioned  

The search results are influenced both by **Google Books descriptions** *and* the **language used in the Reddit threads** where the books were recommended.

---

## Example

```bash
magpie search "post-apocalyptic but hopeful, not grimdark" -n 1
```

```
1. The Dog Stars — Peter Heller
   Post-apocalyptic romance with suspenseful themes, as a survivor embarks on a perilous journey to find others in a world ravaged by global disaster.
   Amazon: https://www.amazon.com/s?k=The+Dog+Stars+Peter+Heller
```
---
### What Magpie Is (and Isn’t) Good At

**Great for**
- Taste- and vibe-based searches (“hopeful but not grimdark dystopia”)
- Finding overlooked or lesser-known books
- Searching recommendations you already trust

**Not great for**
- Plot-level or ultra-specific queries (“space spiders”) unless they appear in the description or thread text
- Finding books outside the threads you’ve added

---

## Quick Start

```bash
# Add a Reddit thread
magpie add "https://reddit.com/r/books/comments/..."

# Search your saved recommendations
magpie search "obscure historical fiction"

# List all indexed books
magpie list
```

---

## Requirements

* Python 3.12+
* Ollama (for book extraction)

---
## Runs Locally (No GPU Required)

Magpie runs locally on a standard laptop or desktop.  
It was developed and tested on a 2021 MacBook Pro (M1, 16GB RAM) and does not require a GPU.

---

## Installation

```bash
git clone <repo-url>
cd magpie

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

```bash
# Install Ollama and pull a model
brew install ollama
ollama serve  # Run in separate terminal
ollama pull llama3.2
```

---

## Optional: Google Books API Key

By default, Magpie uses unauthenticated Google Books requests.
Heavy usage may be throttled (HTTP 429).

If you hit rate limits, set `GOOGLE_BOOKS_API_KEY` to use your own quota and avoid shared limits.

---

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

---

## How It Works (Briefly)

All data is stored locally (SQLite + ChromaDB); your Reddit threads and embeddings never leave your machine.

### Extraction Flow

1. Parse Reddit thread JSON
2. Extract book mentions from comments using Ollama
3. Enrich book data via Google Books
4. Store books in SQLite and create embeddings in ChromaDB

### Search Flow

1. Encode the query with sentence-transformers
2. Retrieve similar book descriptions from ChromaDB
3. Fetch full details from SQLite and display results

---

## Design Decisions

* **Book-centric chunks**: Google Books descriptions provide more stable semantic content than comments alone
* **Thread titles included in embeddings**: Adds context like “overlooked” or “underrated”
* **ChromaDB**: Local-first, no API costs
* **bge-small embeddings**: Fast and lightweight

---

## License

MIT


