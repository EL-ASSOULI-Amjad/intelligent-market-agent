import feedparser
from datetime import datetime, timezone
import json
def fetch_feed(url: str) -> list[dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        articles.append({
            'headline': entry.get('title', ''),
            'url': entry.get('link', ''),
            'summary': entry.get('summary', ''),
            'published_at': _parse_date(entry),
            'source': feed.feed.get('title', url),
        })
    json_str = json.dumps(articles, indent=4)
    with open("scrapped_news.json", "w") as f:
        f.write(json_str)
 
def _parse_date(entry) -> datetime:
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)