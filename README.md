# App Finder 100k

> Discover low-to-mid install Android apps with signal, not noise.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](#tech-stack)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](#tech-stack)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue?style=for-the-badge)](LICENSE)
[![Data Source](https://img.shields.io/badge/Data-Google%20Play%20Scraper-34A853?style=for-the-badge)](https://pypi.org/project/google-play-scraper/)
[![Storage](https://img.shields.io/badge/Storage-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](#project-structure)

A production-minded Streamlit toolkit for hunting Google Play apps in specific install ranges, de-duplicating findings across sessions, and exporting clean research datasets in one click.

> [!IMPORTANT]
> The app is designed for market research workflows where you need repeatable discovery of apps with constrained install volumes (for example, `10,000+` to `100,000+` segments).

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Key Design Decisions](#key-design-decisions)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Usage](#usage)
- [Configuration](#configuration)
- [License](#license)
- [Contacts](#contacts)
- [Support the Project](#-support-the-project)

## Features

- **Install-range filtering** for both lower and upper bounds (`min_installs`, `max_installs`).
- **Randomized multi-query discovery** over a weighted keyword pool (niche + games + utilities).
- **Multi-locale search strategy** to surface apps from different language/country combinations.
- **Deduplication pipeline** backed by persistent SQLite state (`seen_apps`) so you don’t re-review the same app every run.
- **Detail caching layer** (`app_details_cache`) to reduce repeated API calls and speed up iterative sessions.
- **Parallel metadata fetch** using a thread pool for better throughput on detail lookups.
- **Novelty scoring mode** to rank results by “non-obviousness” instead of raw popularity.
- **DataFrame-based result grid** plus one-click CSV export for downstream BI/analysis.

> [!TIP]
> If you’re in discovery mode, keep `sort_by_novelty` enabled and increase `queries_per_run` first before increasing `search_limit`.

## Tech Stack

- **Language:** Python 3.10+
- **UI layer:** Streamlit
- **Data wrangling:** pandas
- **Data source:** `google-play-scraper`
- **Persistence:** SQLite (`sqlite3` from Python stdlib)
- **Concurrency:** `concurrent.futures.ThreadPoolExecutor`

## Project Structure

```text
.
├── app.py          # Streamlit entrypoint and orchestration
├── ui.py           # Sidebar controls + result rendering
├── scraper.py      # Search, candidate collection, detail fetch pipeline
├── scoring.py      # Novelty score math and sorting helper
├── db.py           # SQLite schema + read/write/cache helpers
├── config.py       # Constants, defaults, keyword pools, locales
├── requirements.txt
├── LICENSE
└── README.md
```

## Key Design Decisions

1. **Stateful dedup over stateless scraping**
   - A persistent `seen_apps` table avoids rediscovery churn and keeps each run high signal.
2. **Cache-first detail fetch**
   - App details are cached with TTL semantics to cut API pressure and improve UX responsiveness.
3. **Weighted keyword sampling**
   - Niche terms are intentionally weighted to increase odds of finding less-saturated apps.
4. **Bounded parallelism**
   - Worker count scales with expected result volume to keep performance predictable.
5. **Post-fetch install filtering**
   - Install thresholds are enforced after details lookup because install metadata quality can vary at search stage.

> [!NOTE]
> Internal display labels are currently Russian in the UI/data columns. This is expected behavior and does not affect export integrity.

## Getting Started

### Prerequisites

Install the following locally:

- **Python** `3.10` or newer
- **pip** (bundled with most Python distributions)
- Optional but recommended:
  - `venv` for isolated environments
  - `git` for source sync

### Installation

```bash
# 1) Clone repository
git clone https://github.com/<your-org>/App-Finder-100k.git
cd App-Finder-100k

# 2) Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4) Run the app
streamlit run app.py
```

> [!WARNING]
> First run may feel slower because caches are cold and the app is populating local SQLite state.

## Testing

There is currently no dedicated automated test suite in this repository. Use the following quality gates locally:

```bash
# Sanity check Python syntax
python -m compileall .

# Optional: run with Streamlit and manually validate core flows
streamlit run app.py
```

Manual validation checklist:

- Sidebar controls update search behavior correctly.
- `Найти` triggers fresh candidate discovery.
- Install range filter excludes out-of-band apps.
- CSV export downloads expected columns.
- “Очистить историю” resets dedup state.

## Deployment

For lightweight deployment, Streamlit Community Cloud or a small VM/container works well.

### Minimal production approach

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker-style deployment outline

```bash
# Example runtime command (assuming image already built)
docker run --rm -p 8501:8501 -v $(pwd):/app -w /app python:3.11-slim \
  bash -lc "pip install -r requirements.txt && streamlit run app.py --server.address 0.0.0.0"
```

> [!CAUTION]
> SQLite is file-based and great for single-instance deployment. For horizontal scaling, migrate state/cache tables to a centralized store.

## Usage

```bash
# Start UI
streamlit run app.py

# In the sidebar:
# 1) Set min/max installs
# 2) Tune query depth and run count
# 3) Toggle novelty sorting
# 4) Click "Найти"
# 5) Export CSV when results look good
```

Typical workflow:

1. Start with conservative filters (`min_installs=10_000`, `max_installs=200_000`).
2. Run several iterations to enrich the dedup database.
3. Enable novelty sort for “hidden gems” style prioritization.
4. Export CSV and feed it into your analysis pipeline.

## Configuration

Project configuration lives in `config.py`.

Key knobs:

- `DEFAULT_MIN_INSTALLS`, `DEFAULT_MAX_INSTALLS`
- `DEFAULT_RESULTS_LIMIT`, `DEFAULT_SEARCH_DEPTH`, `DEFAULT_QUERIES_PER_RUN`
- `DEFAULT_WORKERS`
- `SEARCH_LOCALES`
- `GAME_KEYWORDS`, `NICHE_KEYWORDS`, `UTILITY_KEYWORDS`, `ALL_KEYWORDS`
- `CACHE_TTL_SEARCH`, `CACHE_TTL_DETAILS`
- `DB_PATH`

No `.env` is required right now.

> [!NOTE]
> If you need environment-driven config, the clean extension path is to introduce a small settings layer (e.g., `pydantic-settings` or `os.getenv`) and keep `config.py` as defaults.

## License

This project is distributed under the **GPL-3.0** license. See `LICENSE` for full legal terms.

## Contacts

Maintainer and channels are listed below.

## ❤️ Support the Project

If you find this tool useful, consider leaving a ⭐ on GitHub or supporting the author directly:

[![Patreon](https://img.shields.io/badge/Patreon-OstinFCT-f96854?style=flat-square&logo=patreon)](https://www.patreon.com/OstinFCT)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-fctostin-29abe0?style=flat-square&logo=ko-fi)](https://ko-fi.com/fctostin)
[![Boosty](https://img.shields.io/badge/Boosty-Support-f15f2c?style=flat-square)](https://boosty.to/ostinfct)
[![YouTube](https://img.shields.io/badge/YouTube-FCT--Ostin-red?style=flat-square&logo=youtube)](https://www.youtube.com/@FCT-Ostin)
[![Telegram](https://img.shields.io/badge/Telegram-FCTostin-2ca5e0?style=flat-square&logo=telegram)](https://t.me/FCTostin)
