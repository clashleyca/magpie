"""Book extraction via LLM."""

import json
import re
from typing import Any, Optional

import requests


_ollama_warned = False


class BookExtractor:
    """Extract book titles and authors from text using Ollama LLM."""

    def __init__(self, model: str = "llama3.2", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url

    def extract(self, text: str) -> list[dict[str, Any]]:
        """Extract book titles and authors from text."""
        return extract_books_from_text(text, ollama_model=self.model)

    def summarize(self, description: str) -> Optional[str]:
        """Summarize a book description."""
        return summarize_description(description, ollama_model=self.model)


def extract_books_from_text(text: str, ollama_model: str = "llama3.2") -> list[dict[str, Any]]:
    """Use Ollama to extract book titles and authors from text."""
    global _ollama_warned

    prompt = f"""Extract book titles and authors from this text. STRICT RULES:
- ONLY extract books that are EXPLICITLY mentioned by name in the text
- Do NOT invent or guess books - if unsure, skip it
- Do NOT include books from your training data that aren't in the text
- If no books are clearly mentioned, return []

Return JSON array: [{{"title": "exact title from text", "author": "author if mentioned"}}]

Text: {text}

JSON:"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": ollama_model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()["response"]

        # Extract JSON from response - handle both array and single object
        result = result.strip()

        # Try array first
        json_match = re.search(r"\[.*\]", result, re.DOTALL)
        if json_match:
            books = json.loads(json_match.group())
            return _filter_valid_books(books, source_text=text)

        # Try single object
        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        if json_match:
            book = json.loads(json_match.group())
            if isinstance(book, dict):
                return _filter_valid_books([book], source_text=text)
    except requests.ConnectionError:
        if not _ollama_warned:
            print("\nError: Cannot connect to Ollama. Is it running? (ollama serve)")
            _ollama_warned = True
    except requests.RequestException as e:
        if not _ollama_warned:
            print(f"\nError calling Ollama: {e}")
            _ollama_warned = True
    except (json.JSONDecodeError, KeyError):
        pass  # LLM returned non-JSON, skip this comment

    return []


def _filter_valid_books(books: list[dict[str, Any]], source_text: str = "") -> list[dict[str, Any]]:
    """Filter out invalid book entries and validate against source text."""
    invalid_values = {"null", "unknown", "n/a", "none", ""}
    valid = []
    source_lower = source_text.lower()

    for book in books:
        if not isinstance(book, dict):
            continue
        title = (book.get("title") or "").strip()
        title_lower = title.lower()

        if not title or title_lower in invalid_values:
            continue

        # Validate: at least part of the title should appear in source text
        if source_text:
            # Check if any significant word from title appears in source
            title_words = [w for w in title_lower.split() if len(w) > 3]
            if title_words and not any(word in source_lower for word in title_words):
                continue  # Likely hallucinated

        valid.append(book)
    return valid


def summarize_description(description: str, ollama_model: str = "llama3.2") -> Optional[str]:
    """Use Ollama to create a concise 1-2 sentence summary of a book description."""
    if not description or len(description) < 50:
        return description  # Already short enough

    prompt = f"""Summarize this book description in 1-2 sentences (max 150 characters). Focus on genre and core premise. No spoilers. Reply with ONLY the summary, no preamble.

Description: {description}

Summary:"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": ollama_model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()["response"].strip()
        # Clean up any quotes the LLM might add
        result = result.strip('"\'')
        # Remove common LLM preamble patterns
        preamble_patterns = [
            "Here is a summary",
            "Here's a summary",
            "Summary:",
            "Here is the summary",
            "Here's the summary",
        ]
        for pattern in preamble_patterns:
            if result.lower().startswith(pattern.lower()):
                result = result[len(pattern):].lstrip(": \n")
                break
        # Truncate if still too long
        if len(result) > 200:
            result = result[:197] + "..."
        return result
    except requests.RequestException:
        return None
