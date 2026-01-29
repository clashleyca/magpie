"""Embedding and text processing for books."""

import os

# Set environment variables BEFORE any transformers imports
os.environ["TQDM_DISABLE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["SAFETENSORS_FAST_GPU"] = "1"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"

_model = None
_logging_initialized = False


def _init_logging():
    """Suppress noisy output from transformers/torch (called once before first encode)."""
    global _logging_initialized
    if _logging_initialized:
        return
    _logging_initialized = True

    import logging
    import warnings

    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore")  # Suppress all warnings
    logging.getLogger("transformers").setLevel(logging.CRITICAL)
    logging.getLogger("sentence_transformers").setLevel(logging.CRITICAL)
    logging.getLogger("torch").setLevel(logging.CRITICAL)
    logging.getLogger("safetensors").setLevel(logging.CRITICAL)
    logging.getLogger("huggingface_hub").setLevel(logging.CRITICAL)


def get_model(model_name: str = DEFAULT_MODEL):
    """Get or initialize the sentence transformer model."""
    import io
    import sys

    global _model
    if _model is None:
        _init_logging()

        # Suppress stderr during import (catches HF warnings)
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            from sentence_transformers import SentenceTransformer
        finally:
            sys.stderr = old_stderr

        # Suppress stdout/stderr during model loading (catches LOAD REPORT messages)
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            _model = SentenceTransformer(model_name)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
    return _model


_first_encode = True


def encode(text: str, model_name: str = DEFAULT_MODEL) -> list[float]:
    """Encode text into an embedding vector."""
    import io
    import sys

    global _first_encode
    model = get_model(model_name)

    # Suppress output on first encode (LOAD REPORT can appear here)
    if _first_encode:
        _first_encode = False
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            embedding = model.encode(text, normalize_embeddings=True)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
    else:
        embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def encode_batch(
    texts: list[str], model_name: str = DEFAULT_MODEL
) -> list[list[float]]:
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
