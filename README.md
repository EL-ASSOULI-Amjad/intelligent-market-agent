# Market Intelligence Agent

An agent-based system for gathering and analyzing market/financial data — news scraping, NLP, econometrics, microstructure analysis, and graph-based reasoning, tied together through a pipeline and exposed via an API.

## Status

Early scaffolding stage. The project structure is laid out, and the first working piece — an RSS news scraper — is in progress.

## Current Progress

### Working
- **RSS feed fetching** ([scrapping_RSS.py](src/agent/scrapping/scrapping_RSS.py)): given a feed URL, pulls entries via `feedparser` and normalizes each into a dict with `headline`, `url`, `summary`, `published_at`, and `source`, then writes them to `scrapped_news.json`.
- **Feed list** ([feeds.json](src/agent/scrapping/feeds.json)): registry of named RSS sources to pull from (currently just Nasdaq Markets).
- **Runner script** ([RSS_links_scraper.py](src/agent/scrapping/RSS_links_scraper.py)): loops over `feeds.json` and fetches each feed.

### Known issues
- The scraper run in the last commit failed (per commit message) — needs debugging.
- Only one feed source is registered so far; more need to be added to `feeds.json`.
- No persistence layer yet — output is a flat local JSON file, no dedup/versioning across runs.

### Not started
The following modules exist as empty scaffolding, reserved for future work:

| Path | Intended purpose |
|---|---|
| `src/agent/nlp/` | NLP processing of scraped text (sentiment, entity extraction, etc.) |
| `src/agent/econometrics/` | Quantitative/statistical modeling |
| `src/agent/microstructure/` | Market microstructure analysis |
| `src/agent/graph/` | Graph-based relationship modeling |
| `src/agent/pipeline/` | Orchestration tying scraping → processing → storage together |
| `src/agent/api/` | External-facing API |
| `src/dags/` | Scheduled/orchestrated workflows (e.g. Airflow) |
| `src/notebooks/` | Exploratory analysis notebooks |
| `src/scripts/` | Standalone utility scripts |

## Project Structure

```
src/
├── agent/
│   ├── api/              # (empty) external API
│   ├── econometrics/      # (empty) quantitative models
│   ├── graph/             # (empty) graph-based analysis
│   ├── microstructure/     # (empty) market microstructure analysis
│   ├── nlp/               # (empty) NLP processing
│   ├── pipeline/          # (empty) orchestration
│   └── scrapping/         # RSS news scraper (active)
│       ├── feeds.json
│       ├── RSS_links_scraper.py
│       ├── scrapping_RSS.py
│       └── testing.ipynb
├── dags/                  # (empty) scheduled workflows
├── notebooks/             # (empty) exploratory notebooks
└── scripts/               # (empty) utility scripts
```

## Requirements

- Python 3.11+
- [`feedparser`](https://pypi.org/project/feedparser/)

## Next Steps
- Fix the failing scraper run.
- Add more RSS sources to `feeds.json`.
- Start wiring scraped output into a storage/pipeline step instead of a flat JSON file.
