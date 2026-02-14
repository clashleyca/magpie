# Magpie

Search the book recommendations you already trust.

---

## Why

Every book recommendation tool surfaces the same bestsellers. But I have years of saved Reddit threads — *"books I've never heard of," "overlooked favorites," "the best novel you've read"* — full of thoughtful suggestions from real people for books that don't show up on Amazon, Goodreads, or ChatGPT.

Magpie lets me search *only that pile* using natural prompts. It's semantic search over recommendations I already trust, not the whole internet.

---

## Example

```bash
magpie search "spaceship crew stranded"
```

```
3. The Wreck of the River of Stars — Michael Flynn
   Far-future space opera set on a luxury liner struggling to adapt to new technology, exploring themes of identity and tradition amidst catastrophic change.
   Amazon: https://www.amazon.com/s?k=The%20Wreck%20of%20the%20River%20of%20Stars%20Michael%20Flynn

2. The Black Destroyer — Jake Elwood
   A lone captain seeks revenge against an enemy ship after being stranded on a lawless space station, where he must scrounge up a crippled warship and a crew to take down his pursuer.
   Amazon: https://www.amazon.com/s?k=The%20Black%20Destroyer%20Jake%20Elwood

1. We Who Are About To... — Joanna Russ
   A stranded spaceship passenger must choose between survival and dignity in a desperate bid for self-preservation on an unforgiving alien world.
   Amazon: https://www.amazon.com/s?k=We%20Who%20Are%20About%20To...%20Joanna%20Russ
```

```bash
magpie search "science fiction detective"
```

```
3. Come, Hunt an Earthman — Philip E. High
   A human hunter must navigate a deadly game where the prey is intelligent and cunning, turning the tables on traditional predator-prey dynamics.
   Amazon: https://www.amazon.com/s?k=Come%2C%20Hunt%20an%20Earthman%20Philip%20E.%20High

2. Pattern Recognition — William Gibson
   A sensitivity-obsessed ad executive becomes entangled in a global quest for a mysterious filmmaker's lost footage.
   Amazon: https://www.amazon.com/s?k=Pattern%20Recognition%20William%20Gibson

1. The Caves of Steel — Isaac Asimov
   Robot scientist is murdered on a Spacer ship, prompting detective Elijah Baley to team up with his robot partner R.
   Amazon: https://www.amazon.com/s?k=The%20Caves%20of%20Steel%20Isaac%20Asimov
```

---

## What It Does

Magpie:

1. **Extracts books** from Reddit recommendation threads using an LLM
2. **Enriches metadata** via Google Books (descriptions, ISBNs, Amazon links)
3. **Enables semantic search** over those recommendations (not the whole internet)
4. **Deduplicates books** across threads and tracks where each one was mentioned

The search results are influenced both by **Google Books descriptions** *and* the **language used in the Reddit threads** where the books were recommended.

---

## Quick Start

```bash
# Add a Reddit thread
magpie add "https://reddit.com/r/books/comments/..."

# Search your saved recommendations
magpie search "religious figures and dark magic"

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
```

### Searching

```bash
magpie search "obscure historical fiction with magic"
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


