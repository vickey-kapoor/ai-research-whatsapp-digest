"""Fetch AI research posts from major AI lab blogs."""

from datetime import datetime
from typing import Optional
import socket

import feedparser

# Timeout for feedparser requests (seconds)
REQUEST_TIMEOUT = 30


# Blog RSS feeds from major AI labs
BLOG_FEEDS = {
    "Google AI": "https://blog.google/technology/ai/rss/",
    "DeepMind": "https://deepmind.google/blog/rss.xml",
    "Meta AI": "https://ai.meta.com/blog/rss/",
}

# Keywords for filtering AI Agents & Reasoning content
AGENT_REASONING_KEYWORDS = [
    "agent",
    "reasoning",
    "chain of thought",
    "cot",
    "tool use",
    "planning",
    "multi-agent",
    "agentic",
    "autonomous",
    "llm",
    "language model",
    "gemini",
    "llama",
]


def _matches_keywords(text: str) -> bool:
    """Check if text contains any agent/reasoning keywords."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in AGENT_REASONING_KEYWORDS)


def _parse_date(entry: dict) -> str:
    """Parse publication date from feed entry."""
    # Try common date fields
    for field in ["published", "updated", "created"]:
        date_str = entry.get(field, "")
        if date_str:
            try:
                # feedparser provides parsed time tuples
                parsed = entry.get(f"{field}_parsed")
                if parsed:
                    return datetime(*parsed[:6]).isoformat()
            except (TypeError, ValueError):
                pass
    return datetime.now().isoformat()


def _fetch_single_feed(source: str, url: str, max_per_source: int) -> list[dict]:
    """Fetch posts from a single RSS feed."""
    try:
        # Set socket timeout for feedparser
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(REQUEST_TIMEOUT)
        try:
            feed = feedparser.parse(url)
        finally:
            socket.setdefaulttimeout(old_timeout)

        if feed.bozo and not feed.entries:
            print(f"Warning: {source} feed parse error")
            return []

        posts = []
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")

            # Filter for agent/reasoning relevance (be more lenient for major labs)
            if not _matches_keywords(title) and not _matches_keywords(summary):
                continue

            # Clean summary (remove HTML tags if present)
            summary = summary.replace("<p>", "").replace("</p>", " ")
            summary = summary.replace("<br>", " ").replace("<br/>", " ")
            summary = " ".join(summary.split())  # Normalize whitespace
            if len(summary) > 500:
                summary = summary[:497] + "..."

            post = {
                "title": title.strip(),
                "description": summary.strip(),
                "source": source,
                "url": entry.get("link", ""),
                "published_at": _parse_date(entry),
                "type": "research",
                "authors": source,  # Blog posts typically don't list individual authors
                "topics": ["AI Agents", "Reasoning"],
            }
            posts.append(post)

            if len(posts) >= max_per_source:
                break

        return posts

    except socket.timeout:
        print(f"Error: {source} blog request timed out")
        return []
    except Exception:
        print(f"Error: Failed to fetch {source} blog")
        return []


def fetch_blog_posts(max_results: int = 5) -> list[dict]:
    """
    Fetch recent AI Agents & Reasoning posts from major AI lab blogs.

    Args:
        max_results: Maximum total number of posts to return

    Returns:
        List of normalized post dictionaries
    """
    all_posts = []
    max_per_source = max(1, max_results // len(BLOG_FEEDS) + 1)

    for source, url in BLOG_FEEDS.items():
        posts = _fetch_single_feed(source, url, max_per_source)
        all_posts.extend(posts)

    # Sort by published date (most recent first)
    all_posts.sort(
        key=lambda x: x.get("published_at", ""),
        reverse=True,
    )

    return all_posts[:max_results]
