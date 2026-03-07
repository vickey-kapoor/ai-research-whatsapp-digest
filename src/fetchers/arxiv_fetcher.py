"""Fetch AI research papers from arXiv."""

from datetime import datetime, timedelta
from typing import Optional
import urllib.parse
import socket

import feedparser


# Use HTTPS for secure communication
ARXIV_API_URL = "https://export.arxiv.org/api/query"

# Timeout for feedparser requests (seconds)
REQUEST_TIMEOUT = 30

# Keywords for AI Agents & Reasoning research
AGENT_REASONING_KEYWORDS = [
    "AI agent",
    "autonomous agent",
    "reasoning",
    "chain of thought",
    "CoT",
    "ReAct",
    "tool use",
    "planning",
    "multi-agent",
    "agentic",
]


def fetch_arxiv_papers(max_results: int = 5) -> list[dict]:
    """
    Fetch recent AI Agents & Reasoning papers from arXiv.

    Args:
        max_results: Maximum number of papers to return

    Returns:
        List of normalized paper dictionaries
    """
    # Build search query for AI/ML categories with agent/reasoning focus
    categories = "(cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.MA)"
    keywords = " OR ".join(f'all:"{kw}"' for kw in AGENT_REASONING_KEYWORDS[:5])
    query = f"{categories} AND ({keywords})"

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results * 2,  # Fetch extra to filter
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"

    try:
        # Set socket timeout for feedparser
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(REQUEST_TIMEOUT)
        try:
            feed = feedparser.parse(url)
        finally:
            socket.setdefaulttimeout(old_timeout)

        if feed.bozo and not feed.entries:
            print("Warning: arXiv feed parse error")
            return []

        papers = []
        for entry in feed.entries[:max_results]:
            # Extract authors
            authors = ", ".join(
                author.get("name", "Unknown") for author in entry.get("authors", [])
            )
            if len(authors) > 100:
                authors = authors[:97] + "..."

            # Parse published date
            published = entry.get("published", "")
            try:
                published_dt = datetime.strptime(published[:10], "%Y-%m-%d")
                published_at = published_dt.isoformat()
            except (ValueError, IndexError):
                published_at = datetime.now().isoformat()

            # Extract categories/topics
            categories = [tag.get("term", "") for tag in entry.get("tags", [])]
            topics = [c for c in categories if c.startswith("cs.")]

            # Clean abstract
            abstract = entry.get("summary", "").replace("\n", " ").strip()
            if len(abstract) > 500:
                abstract = abstract[:497] + "..."

            paper = {
                "title": entry.get("title", "").replace("\n", " ").strip(),
                "description": abstract,
                "source": "arXiv",
                "url": entry.get("link", ""),
                "published_at": published_at,
                "type": "research",
                "authors": authors,
                "topics": topics,
            }
            papers.append(paper)

        return papers

    except socket.timeout:
        print("Error: arXiv request timed out")
        return []
    except Exception:
        print("Error: Failed to fetch arXiv papers")
        return []
