# Game Patch Notes Project

## Overview

This project aims to analyze **game patch notes** to gain insights into how games evolve over time, how developers iterate on gameplay, and how user experience is affected by changes. 
The first step in this project involves **selecting appropriate data sources** and **building a dataset** from them.

---

# 1.  Data Source Selection

### 📌 Data Source: Steam Platform

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

## Data Access & Limitations

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


We plan to **build a local dataset** representing the Steam game catalog, from which we can later sample games for patch note analysis.

---

## A. Create the **Local Dataset** 

This step builds a local dataset of Steam games by querying the `appdetails` API and collecting selected metadata.

1. **Initial App List Retrieval**
   * Download the full list of app IDs from the Steam endpoint (includes games and non-game apps).
   * Save the list to [`applist.json`](./applist.json).

2. **Filtering and Metadata Collection**

   * For each app ID in the list:

     * Query the `appdetails` API individually.
     * Record every query in [`queries.json`](./queries.json) to prevent redundant calls.
     * Check whether the app is categorized as a **game**.
     * If it is a game:

       * Extract basic metadata and store it locally in the folder [./raw_metadata_dataset/](./raw_metadata_dataset/).
       * Filenames follow the format: `{appid}__{name}.json`.
       * At this stage, only high-level metadata is collected (no patch notes or extended data).

   * This step is implemented in a Jupyter notebook: [game_metadata_extraction.ipynb](./game_metadata_extraction.ipynb).
    > **Note:** Due to Steam API rate limits (100,000 calls/day, \~200 every 5 minutes), the script is designed to run incrementally over several days. It is intended to be launched once per app ID list.

3. **Metadata Formatting**

   * After metadata extraction, format the dataset as one CSV file: [games_metadata.csv](./games_metadata.csv)
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
   * This step is implemented in a Jupyter notebook: [appdetails_to_csv.ipynb](./appdetails_to_csv.ipynb).


---

# Current Status and TODO

* ✅ Initial app ID list retrieved (257,148 entries total)
* ✅ Incremental filtering process implemented to extract game metadata
* ✅ Metadata stored in structured JSON files for local use
  * Aug 8, 2025: 27% of queries made
  * Aug 15, 2025, 72% of queries made
* ✅ Format selected metadata from individual JSON files into one csv


### 🛠️ TODO:
* ⬜ Script to analyze the selected metadata (descriptive stats)
* ⬜ Fetch complementary metadata for each game? (e.g., users, hours played)
* ⬜ Write a short update script to refresh the dataset with **new entries** without re-fetching the entire list.
* ⬜ Begin defining sampling strategy for selecting games from the dataset for patch note analysis.

### 🤔 Related questions:
* 99% of games on Steam are indie games, but how much game time / size of user-base compared to AAA games?
* Can we use the raw game metadata to identify game clusters (PCA)?