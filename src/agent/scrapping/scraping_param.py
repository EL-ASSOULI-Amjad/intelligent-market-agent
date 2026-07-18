"""Polite RSS ingestion: conditional requests, per-feed state, dedupe.

Run from src/:  python -m agent.scrapping.RSS_links_scraper
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import feedparser

from agent.pipeline.storing_results import load_state, save_state, upsert

USER_AGENT = "NewsSignalBot/1.0 "
FEEDS_FILE = Path(__file__).resolve().parent / "feeds.json"

RETRYABLE = {429, 500, 502, 503, 504}


def load_feeds() -> list[str]:
    data = json.loads(FEEDS_FILE.read_text(encoding="utf-8"))
    return data                                    # ["https://...", ...]


def _parse_date(entry) -> str | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()


def _header(feed, name: str) -> str | None:
    value = getattr(feed, name, None)
    if isinstance(value, str):
        return value
    return getattr(feed, "headers", {}).get(name)


def fetch_feed(url: str, etag: str | None = None,
               modified: str | None = None) -> dict:
    feed = feedparser.parse(url, agent=USER_AGENT, etag=etag, modified=modified)
    status = getattr(feed, "status", None)

    if status == 304:
        return {"status": 304, "articles": [], "etag": etag,
                "modified": modified, "bozo": False}

    if status in RETRYABLE:
        raise RuntimeError(f"retryable status {status}")
    if status in (401, 403, 404, 410):
        raise RuntimeError(f"blocked or gone: status {status}")

    articles = [{
        "id": entry.get("id") or entry.get("link"),
        "headline": entry.get("title", ""),
        "url": entry.get("link", ""),
        "summary": entry.get("summary", ""),
        "published_at": _parse_date(entry),
        "source": feed.feed.get("title", url),
    } for entry in feed.entries]

    return {
        "status": status,
        "articles": articles,
        "etag": _header(feed, "etag"),
        "modified": _header(feed, "modified"),
        "bozo": bool(feed.bozo),
    }


def main() -> None:
    state = load_state()

    for url in load_feeds():
        saved = state.get(url, {})
        try:
            result = fetch_feed(url, saved.get("etag"), saved.get("modified"))
        except Exception as exc:
            print(f"[skip] {url} -> {exc}")
            continue

        state[url] = {"etag": result["etag"], "modified": result["modified"]}
        added = upsert(result["articles"])
        flag = " (malformed XML)" if result["bozo"] else ""
        print(f"[ok]   {url} status={result['status']} new={added}{flag}")

    save_state(state)


if __name__ == "__main__":
    main()