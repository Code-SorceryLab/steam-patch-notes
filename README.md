# Game Patch Notes Project

## Overview

This project aims to analyze **game patch notes** to gain insights into how games evolve over time, how developers iterate on gameplay, and how user experience is affected by changes.
The project builds a four-stage pipeline: collecting news posts from Steam, filtering them down to patch notes using keywords, classifying each change with an LLM, and exposing the resulting dataset through a searchable web application — **PatchSense**.

---

# 1.  Data Source Selection

### Data Source: Steam Platform

We chose **Steam** as our only data source. Steam is a digital distribution platform developed by Valve Corporation, and it's the **largest global platform for video games**.

### How representative and relevant is it?
* **Massive Coverage**: As of 2021, Steam hosted over **30,000 games**, ranging from AAA titles to indie releases.
* **High Engagement**: In 2021, the platform recorded **132 million monthly active users**.
* Most **major games** are available on Steam.
* The platform is **open to indie developers** (99% of games on steams are indie games), ensuring a broad representation of genres and development styles.


### Relevance for our study
* It provides a **comprehensive sampling frame** of the gaming ecosystem.
* Focusing on a single, dominant platform allows us to standardize the data retrieval process across a wide range of games and patch histories.

---


# 2. Data Access & Limitations

### Access Method

We use the official **Steam Web API** to query data.

* API Documentation: [https://steamcommunity.com/dev](https://steamcommunity.com/dev)
* API Terms of Use: [https://steamcommunity.com/dev/apiterms](https://steamcommunity.com/dev/apiterms)

**Permissions**: usage of the Steam Web API is permitted under their terms of use, provided we remain compliant:
[Steam Web API Terms](https://steamcommunity.com/dev/apiterms)



### Limitations and Mitigations

| Limitation                                                     | Mitigation                                                                                  |
|----------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **API Rate Limit**: 100,000 calls/day (~200 calls/5 min)       | Implement an automated, incremental retrieval process to distribute requests across the day |
| **Data Noise**: Many app IDs are not games (DLCs, tools, etc.) | Implement filtering logic to include only actual games                                      |
| **Inconsistent Metadata**: Duplicate entries, changing appIDs  | Add validation and logging steps to identify inconsistencies                                |


We built a **local dataset** representing the Steam game catalog, from which we can sample games for patch note analysis.

---
# 3. Pipeline

### A. Create the **Local Dataset**
This step builds a local dataset of Steam games by querying the `appdetails` API and collecting selected metadata.

1. **Initial App List Retrieval**
   * Download the full list of app IDs from the Steam endpoint (includes games and non-game apps).
   * Save the list to [applist.json](./applist.json).

2. **Filtering and Metadata Collection**

   * For each app ID in the list:

     * Query the `appdetails` API individually.
     * Record every query in [queries.json](./queries.json) to prevent redundant calls.
     * Check whether the app is categorized as a **game**.
     * If it is a game:

       * Extract basic metadata and store it locally in the folder [./appdetails/](./appdetails/).
       * Filenames follow the format: `{appid}__{name}.json`.
       * At this stage, only high-level metadata is collected (no patch notes or extended data).

   * This step is implemented in a Jupyter notebook: [game_metadata_extraction.ipynb](./scripts/game_metadata_extraction.ipynb).
    > **Note:** Due to Steam API rate limits (100,000 calls/day, \~200 every 5 minutes), the script is designed to run incrementally over several days. It is intended to be launched once per app ID list.

3. **Metadata Formatting**

   * After metadata extraction, format the dataset as one CSV file: [games_metadata.csv](./output/games_metadata.csv)
   * Each row represents a game, with the following metadata fields as columns:
     * _name,
     steam_appid,
     required_age,
     is_free,
     number_dlc,
     developers,
     publishers,
     price_currency,
     price_initial,
     price_final,
     windows,
     mac,
     linux,
     metacritic_score,
     categories,
     genres,
     recommendations_total,
     achievements_total,
     release_date_
   * The resulting CSV file is compatible with our internal **sampling tool**.
   * This step is implemented in a Jupyter notebook: [appdetails_to_csv.ipynb](./scripts/appdetails_to_csv.ipynb).
4. **Descriptive Stats** of the selected metadata
   * The columns of the CSV file are analysed to have insights on their content
   * This is implemented in a Jupyter notebook: [dataset_overview.ipynb](./scripts/dataset_overview.ipynb).



---

### B. Patch Note Collection & Keyword Filtering

This step fetches all news posts for each game in the dataset and filters them to isolate genuine patch notes.

1. **News Collection** via the Steam `GetNewsForApp` API.
   * Fetched news for all games in `output/games_metadata.csv`
   * **Result:** 145,622 games · 1,873,879 news items
   * Output: `patches/raw_news/{appid}.json`
   * Implemented in `scripts/get_news_script/`

2. **Keyword Filtering** to separate patch notes from general announcements, promotions, etc.
   * Keywords matched: `"patch notes"`, `"hotfix"`, `"changelog"`, `"bug fix"` (and others)
   * High recall approach — intentionally broad to avoid missing genuine patches
   * **Result:** 73,744 games · 1,085,168 items retained (57.8%)
   * Output: `patches/filtered_patches/{appid}.json`

3. **Cleaning** — HTML stripping and text normalization.
   * Output: `patches/cleaned_patches/{appid}.json`
   * Implemented in `scripts/cleaning_script/`

> **Note:** Keyword filtering achieves high recall but lower precision — promotional posts that mention patch-related words are retained. This false positive rate (~24.7%) is resolved in Stage C.

---

### C. LLM Classification

Keyword-filtered notes are passed through **Gemini 2.5 Flash-Lite** (`temp=0.0`, JSON output) to verify, extract, and classify each change statement.

**Three tasks per note:**
1. **Verify** — is this actually a patch note?
2. **Extract** — identify individual change statements within the note
3. **Classify** each statement as one of:

| Tag | Meaning | Example |
|---|---|---|
| `bug` | Crash fixes, broken behavior | `"Fixed a crash when opening the scoreboard"` |
| `feature` | New content, modes, mechanics | `"Added three new playable heroes"` |
| `balance_change` | Stat/cooldown/cost adjustments | `"Reduced cooldown 13s → 10s"` |

**Output format** (`patches/llm_filtered_patches/{appid}.json`):
```json
{
  "appId": "70",
  "notes": [{
    "title": "October 2, 2024 Update",
    "tags": [
      {"bug": "Fixed HLTV startup crashes"},
      {"feature": "Enabled /LARGEADDRESSAWARE to support mods with large memory requirements"}
    ]
  }]
}
```

**Hybrid processing architecture** (`scripts/llm_filtering_script/`):

| Mode | Scale | Speed | Cost |
|---|---|---|---|
| Sequential (`filter_patch_notes.py`) | ~200 notes | Real-time | Higher |
| Batch API (`batch_process/process_batch.py`) | ~10,000 notes | Hours | 50% cheaper |

Both modes ran simultaneously on non-overlapping file subsets. Unique note keys allow resume-from-failure.

**Result:** 68,043 games · 817,765 patch notes · 8.3M tags
> 24.7% of keyword-filtered items were confirmed as false positives by the LLM and excluded.

---

### D. Web Application — PatchSense

PatchSense is a FastAPI + SQLite web application that makes the classified dataset searchable and browsable.

![PatchSense](./assets/webapp.png)

**Stack:**
* Backend: FastAPI (`web_application/main.py`), port 8001
* Database: SQLite with FTS5 full-text search (`web_application/database/patchnotes.db`)
* Frontend: HTML/CSS/JS (`web_application/client/`)

**API Endpoints:**

| Endpoint | Description |
|---|---|
| `GET /search` | Full-text keyword search with tag and app_id filters |
| `GET /bugs` | All bug-tagged notes |
| `GET /features` | All feature-tagged notes |
| `GET /balance_changes` | All balance-change-tagged notes |
| `GET /notes` | All notes, paginated |
| `GET /games` | Game list and lookup by name |

**Running locally:**
1. `pip install -r web_application/requirements.txt`
2. `python web_application/ingest.py` *(one-time — loads data into the database)*
3. `python web_application/main.py` → `http://localhost:8001`
4. Open `web_application/client/index.html` in a browser

---

# 4.  Repository Structure

```
steam-patch-notes/
│
├── appdetails/
│   └── {appid}.json
│
├── output/
│   ├── applist.json
│   ├── queries.json
│   ├── games_metadata.csv
│   └── games_metadata_totals.csv
│
├── patches/
│   ├── raw_news/
│   │   └── {appid}.json
│   ├── filtered_patches/
│   │   └── {appid}.json
│   ├── cleaned_patches/
│   │   └── {appid}.json
│   ├── flagged_patches/
│   │   ├── {appid}.json
│   │   └── logs/
│   │       ├── flagged_app_ids.txt
│   │       └── total_flagged_notes.txt
│   └── llm_filtered_patches/
│       └── {appid}.json
│
├── scripts/
│   ├── appdetails_to_csv.ipynb
│   ├── dataset_overview.ipynb
│   ├── game_metadata_extraction.ipynb
│   ├── steamspy_extraction.ipynb
│   ├── cleaning_script/
│   │   ├── file_handler.py
│   │   ├── filter_patch_notes.py
│   │   ├── game_data.py
│   │   ├── run_all.py
│   │   └── strip_html.py
│   ├── find_embedded_data/
│   │   ├── file_handler.py
│   │   ├── find_embedded_data.py
│   │   └── game_data.py
│   ├── get_news_script/
│   │   ├── logs/
│   │   │   ├── output.log
│   │   │   └── skipped_files.txt
│   │   ├── create_json_files.py
│   │   ├── get_news.py
│   │   ├── load_batches.py
│   │   └── session.py
│   ├── additional_scripts/
│   │   ├── add_totals_to_csv.py
│   │   └── total_patch_count.py
│   └── llm_filtering_script/
│       ├── batch_process/
│       │   ├── additional_scripts/
│       │   │   ├── delete_empty_llm_filtered.py
│       │   │   ├── fix_malformed_text.py
│       │   │   ├── hardcode_failed_results.py
│       │   │   ├── merge_failed_results.py
│       │   │   ├── normalize_results.py
│       │   │   ├── norm_results.py
│       │   │   └── resplit_parts.py
│       │   ├── job_id/
│       │   │   ├── job_ids.json
│       │   │   └── upload_ids.json
│       │   ├── config.py
│       │   ├── file_handler.py
│       │   ├── game_data.py
│       │   ├── helper_funtions.py
│       │   ├── job_processor.py
│       │   ├── jsonl_convertor.py
│       │   ├── logger.py
│       │   ├── process_batch.py
│       │   ├── prompts.py
│       │   └── results_parser.py
│       ├── file_handler.py
│       ├── filter_patch_notes.py
│       ├── game_data.py
│       ├── gpt_api.py
│       ├── logger.py
│       └── prompts.py
│
├── statistics/
│   ├── Descriptive Stats/
│   │   ├── desc_stats_news_patches.csv
│   │   ├── missing_values_news.csv
│   │   └── statistics.ipynb
│   └── analysis/
│       ├── games_metadata_totals.csv
│       └── patch_notes_analysis.ipynb
│
├── steamspy_dataset/
│   └── {appid}.json
│
├── web_application/
│   ├── client/
│   │   ├── app.js
│   │   ├── index.html
│   │   └── style.css
│   ├── database/
│   │   └── patchnotes.db
│   ├── routers/
│   │   ├── balance.py
│   │   ├── bugs.py
│   │   ├── features.py
│   │   ├── games.py
│   │   ├── notes.py
│   │   ├── query_utils.py
│   │   └── search.py
│   ├── config.py
│   ├── database.py
│   ├── ingest.py
│   ├── main.py
│   └── requirements.txt
│
├── workflow_design/
│   ├── overview.pdf
│   ├── overview.png
│   ├── stage2.drawio
│   └── stage2.png
│
├── README.md
└── requirements.txt
```


# Current Status

* ✅ Game metadata collected — 145,622 games (`appdetails/`)
* ✅ Metadata formatted to CSV (`output/games_metadata.csv`)
* ✅ Raw news collected — 1,873,879 items across 145,622 games
* ✅ Keyword filtering complete — 1,085,168 items across 73,744 games (57.8% retained)
* ✅ LLM classification complete — 817,765 patch notes · 8.3M tags · 68,043 games
* ✅ PatchSense web application built and functional

### 🛠️ Future Work:
* ⬜ Semantic clustering to find recurring bug patterns across games
* ⬜ Analysis of game evolution over time
* ⬜ RAG-based developer tool: "find how others fixed this bug"