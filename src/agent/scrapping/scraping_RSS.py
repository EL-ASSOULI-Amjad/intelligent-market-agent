import feedparser
from datetime import datetime, timezone

USER_AGENT = "NewsSignalBot/1.0"

def fetch_feed(url: str, etag: str | None = None,
               modified: str | None = None) -> dict:
    feed = feedparser.parse(url, agent=USER_AGENT,
                            etag=etag, modified=modified)

    status = getattr(feed, "status", None)
    if status == 304:
        return {"status": 304, "articles": [], "etag": etag,
                "modified": modified}
    if status in (429, 403, 500, 503):
        raise RuntimeError(f"{url} returned {status}")

    articles = [{
        "id": e.get("id") or e.get("link"),
        "headline": e.get("title", ""),
        "url": e.get("link", ""),
        "summary": e.get("summary", ""),
        "published_at": _parse_date(e),
        "source": feed.feed.get("title", url),
    } for e in feed.entries]

    return {
        "status": status,
        "articles": articles,
        "etag": getattr(feed, "etag", None),
        "modified": getattr(feed, "modified", None),
        "bozo": bool(feed.bozo),
    }


def _parse_date(entry) -> str | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()