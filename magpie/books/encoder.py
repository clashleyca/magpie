"""Embedding and text processing for books."""

import logging
import os
import warnings

# Suppress noisy output before importing transformers/torch
os.environ["TQDM_DISABLE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*layers were not sharded.*")
warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)
logging.getLogger("safetensors").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"

_model = None


def get_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """Get or initialize the sentence transformer model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
    return _model


def encode(text: str, model_name: str = DEFAULT_MODEL) -> list[float]:
    """Encode text into an embedding vector."""
    model = get_model(model_name)
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def encode_batch(texts: list[str], model_name: str = DEFAULT_MODEL) -> list[list[float]]:
    """Encode multiple texts into embedding vectors."""
    model = get_model(model_name)
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def build_book_chunk(
    title: str,
    author: str,
    description: str,
    source_titles: list[str],
) -> str:
    """Build a text chunk for a book suitable for embedding.

    Combines book metadata with source context for better semantic search.
    """
    parts = []

    if source_titles:
        for source_title in source_titles:
            parts.append(f"Recommended for: {source_title}")
            parts.append(f"Category: {source_title}")

    parts.append(f"{title} by {author}")

    if description:
        parts.append(description)

    if source_titles:
        parts.append("Tags: " + ", ".join(source_titles))

    return "\n\n".join(parts)
