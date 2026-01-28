"""Input source adapters for magpie."""

from .reddit import extract_comment_texts, fetch_thread_json, parse_reddit_json

__all__ = ["fetch_thread_json", "parse_reddit_json", "extract_comment_texts"]
