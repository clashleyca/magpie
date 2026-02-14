# Magpie

Search the book recommendations you already trust.

---

## Why I Wrote This (and Why It’s Different)

I have years of saved Reddit threads full of book recommendations — *“books I’ve never heard of,” “overlooked favorites,” “the best novel you’ve read,”* and so on.  
They’re great recommendations… and I almost never remember to look at them when I’m actually trying to find something to read.

I also wanted recommendations that *weren’t* dominated by bestsellers or publisher-driven promotion. Many book recommendation systems surface the same popular titles. In contrast, Reddit recommendation threads — especially ones focused on “overlooked” or “never read” books — are full of thoughtful suggestions from real people, often for books that don’t show up in Amazon, Goodreads, Google, or chatbot recommendations.

**Magpie lets me load those saved Reddit threads and then search *only that pile* of recommendations using natural, vibe-based prompts.**  
Instead of starting from scratch, I’m searching a set of recommendations I already trust.

**In short:** Magpie is semantic search over your saved Reddit recommendation threads (plus Google Books blurbs), not a general book recommender.

---

## Example

```bash
magpie search "religious figures"
```

```
5. A Time for Everything — Karl Ove Knausgaard
   A 16th-century boy's encounter with angels sets him on a lifelong pursuit to understand divine mysteries, reimagining key biblical encounters in a spellbinding narrative.
   Amazon: https://www.amazon.com/s?k=A%20Time%20for%20Everything%20Karl%20Ove%20Knausgaard

4. How are the Mighty Fallen — Thomas Burnett Swann
   Historical fantasy retelling of the David and Jonathan story with a supernatural twist.
   Amazon: https://www.amazon.com/s?k=How%20are%20the%20Mighty%20Fallen%20Thomas%20Burnett%20Swann

3. The Good Man Jesus and the Scoundrel Christ — Philip Pullman
   A young man pines for his brother, who remains oblivious to his feelings, leading to a poignant exploration of love, identity, and mortality.
   Amazon: https://www.amazon.com/s?k=The%20Good%20Man%20Jesus%20and%20the%20Scoundrel%20Christ%20Philip%20Pullman

2. Christ the Lord — Anne Rice
   Historical fiction novel exploring Jesus' life, focusing on his journey from Nazareth to Cana, amidst Roman rule and family pressures.
   Amazon: https://www.amazon.com/s?k=Christ%20the%20Lord%20Anne%20Rice

1. Barabbas — Pär Lagerkvist
   Barabbas is the acquitted; the man whose life was exchanged for that of Jesus of Nazareth, crucified upon the hill of Golgotha.
   Amazon: https://www.amazon.com/s?k=Barabbas%20P%C3%A4r%20Lagerkvist
```

```bash
magpie search "science fiction detective"
```

```
5. All the Colors of Darkness LP — Peter Robinson
   Detective Inspector Annie Cabbot investigates a seemingly suicidal death that turns into a murder mystery, prompting her to call in vacationing Chief Inspector Alan Banks.
   Amazon: https://www.amazon.com/s?k=All%20the%20Colors%20of%20Darkness%20LP%20Peter%20Robinson

4. The Rediscovery of Man — Cordwainer Smith
   Science fiction novel explores a future where an interstellar empire is ruled by virtual immortals who rely on genetically engineered underpeople to serve them.
   Amazon: https://www.amazon.com/s?k=The%20Rediscovery%20of%20Man%20Cordwainer%20Smith

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


