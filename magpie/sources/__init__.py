"""Input source adapters for magpie."""

from .reddit import fetch_thread_json, parse_reddit_json, extract_comment_texts

__all__ = ["fetch_thread_json", "parse_reddit_json", "extract_comment_texts"]
