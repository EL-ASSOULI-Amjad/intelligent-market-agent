"""Storage for scraped articles and per-feed HTTP cache state.

Only this file knows where data lives on disk. To switch to MongoDB
later, rewrite this file and nothing else.
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]   # pipeline → agent → src → root

STATE_FILE = ROOT / "data" / "state" / "feed_state.json"
STORE_FILE = ROOT / "data" / "raw" / "articles.json"


def _ensure_dirs() -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STORE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict:
    """Read a JSON dict. Missing, empty, or broken files return {}."""
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[warn] {path.name} is corrupt, starting fresh")
        path.replace(path.with_suffix(".json.bak"))
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, data: dict) -> None:
    """Write to a temp file first, then rename. Never leaves a half-written file."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    os.replace(tmp, path)


def load_state() -> dict:
    """Return {feed_url: {"etag": ..., "modified": ...}}."""
    return _read_json(STATE_FILE)


def save_state(state: dict) -> None:
    _ensure_dirs()
    _write_json(STATE_FILE, state)


def load_articles() -> dict:
    """Return {article_id: article}."""
    return _read_json(STORE_FILE)


def upsert(articles: list[dict]) -> int:
    """Add new articles to the store, keyed on id. Returns how many were added."""
    _ensure_dirs()
    store = load_articles()

    added = 0
    for article in articles:
        key = article.get("id")
        if not key or key in store:
            continue
        store[key] = article
        added += 1

    if added:
        _write_json(STORE_FILE, store)
    return added