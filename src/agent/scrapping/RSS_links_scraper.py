import json
from scrapping_RSS import fetch_feed
from pathlib import Path

feeds_path = Path(__file__).parent / "feeds.json"


with open(feeds_path, encoding="utf-8") as f:
    FEEDS = json.load(f)

for name, url in FEEDS.items():
    fetch_feed(url)
    if name == "nasdaq_original":
        break