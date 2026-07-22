# Market Intelligence Agent

An agent-based system for gathering and analyzing market/financial data — news scraping, NLP, econometrics, microstructure analysis, and graph-based reasoning, tied together through a pipeline and exposed via an API.

## Status

Early scaffolding stage. `agent` is now a proper Python package, and the RSS scraper has been reworked into a small pipeline: polite fetching (conditional requests + retry handling), persistent per-feed state, and deduped article storage on disk. A first NLP module now runs sentiment analysis over the scraped articles.

## Current Progress

### Working
- **RSS ingestion runner** ([scraping_param.py](src/agent/scrapping/scraping_param.py)): loops over `feeds.json`, fetches each feed via `feedparser` with conditional requests (`etag`/`modified`), skips feeds that 304 (not modified), retries-later on `429/500/502/503/504`, and treats `401/403/404/410` as blocked/gone. Normalizes entries into `id`, `headline`, `url`, `summary`, `published_at`, `source`, then hands them to the pipeline for dedup + storage. Run with `python -m agent.scrapping.scraping_param` from `src/`.
- **Storage layer** ([storing_results.py](src/agent/pipeline/storing_results.py)): owns all on-disk state — per-feed HTTP cache (`data/state/feed_state.json`) and deduped articles keyed by id (`data/raw/articles.json`). Writes are atomic (temp file + rename), and a corrupt JSON file is backed up and reset rather than crashing the run.
- **Feed list** ([feeds.json](src/agent/scrapping/feeds.json)): registry of named RSS sources — currently Reuters Business, FT Home, and CNBC Finance.
- **Standalone fetch helper** ([scraping_RSS.py](src/agent/scrapping/scraping_RSS.py)): a simpler `fetch_feed()` (no state/dedup) that normalizes a single feed's entries. Not currently wired into the runner — looks like an earlier iteration kept alongside the pipeline version.
- **Sentiment analysis** ([articles_analysis.py](src/agent/nlp/articles_analysis.py)): reads `data/raw/articles.json`, runs each article's summary through the `ProsusAI/finbert` model via the Hugging Face Inference API, and writes per-article `positive`/`neutral`/`negative` scores to `data/sentiment_score/sentiment_score.json`. Requires an `HF_TOKEN` in a root `.env` file.

### Known issues
- `scraping_RSS.py` and `scraping_param.py` duplicate most of the same fetch logic; worth consolidating once the pipeline approach is settled.
- Only three feed sources are registered so far; more need to be added to `feeds.json`.
- `articles_analysis.py` re-scores every article on each run (no dedup/caching against already-scored ids) and runs as a top-level script rather than an importable function.

### Not started
The following modules exist as empty scaffolding, reserved for future work:

| Path | Intended purpose |
|---|---|
| `src/agent/econometrics/` | Quantitative/statistical modeling |
| `src/agent/microstructure/` | Market microstructure analysis |
| `src/agent/graph/` | Graph-based relationship modeling |
| `src/agent/api/` | External-facing API |
| `src/dags/` | Scheduled/orchestrated workflows (e.g. Airflow) |
| `src/notebooks/` | Exploratory analysis notebooks |
| `src/scripts/` | Standalone utility scripts |

## Project Structure

```
data/
├── raw/
│   └── articles.json      # deduped article store, keyed by id
├── sentiment_score/
│   └── sentiment_score.json  # per-article positive/neutral/negative scores
└── state/
    └── feed_state.json    # per-feed etag/modified cache
src/
├── agent/
│   ├── __init__.py
│   ├── api/                # (empty) external API
│   ├── econometrics/       # (empty) quantitative models
│   ├── graph/               # (empty) graph-based analysis
│   ├── microstructure/      # (empty) market microstructure analysis
│   ├── nlp/                 # sentiment analysis (active)
│   │   └── articles_analysis.py
│   ├── pipeline/            # storage layer (active)
│   │   ├── __init__.py
│   │   └── storing_results.py
│   └── scrapping/           # RSS news scraper (active)
│       ├── __init__.py
│       ├── feeds.json
│       ├── scraping_param.py   # runner: fetch + state + dedup + storage
│       └── scraping_RSS.py     # standalone fetch helper, not yet wired in
├── dags/                    # (empty) scheduled workflows
├── notebooks/                # (empty) exploratory notebooks
└── scripts/                  # (empty) utility scripts
```

## Requirements

- Python 3.11+
- [`feedparser`](https://pypi.org/project/feedparser/)
- [`huggingface_hub`](https://pypi.org/project/huggingface-hub/)
- [`python-dotenv`](https://pypi.org/project/python-dotenv/)
- A Hugging Face API token, set as `HF_TOKEN` in a root `.env` file

## Next Steps
- Decide between `scraping_RSS.py` and `scraping_param.py` and remove the duplicate.
- Add more RSS sources to `feeds.json`.
- Add dedup/caching to `articles_analysis.py` so already-scored articles aren't re-sent to the model.
- Start building out the econometrics/graph modules on top of the scraped articles and sentiment scores.
