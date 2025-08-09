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

## Retrieval Process Implementation

Implementation is done via a **Jupyter Notebook**: [game_metadata_extraction.ipynb](.?game_metadata_extraction.ipynb).   
Given the **API quota limits** (100,000 calls/day, \~200 every 5 minutes), data collection is implemented incrementally over several days. This script is made to be launched once.

#### Step-by-step Process:

1. **Initial Call**: Retrieve the full list of app IDs from the endpoint (contains both games and other app types), stored in [applist.json](./applist.json)
2. **Filtering**:

   * For each app ID, make an individual query.
     * All made queries are documented in [queries.json](./queries.json) to avoid redundant queries.
   * Check if the entry corresponds to a *game*.
   * If yes, retrieve and store its metadata in a local JSON file:

     * Filename format: `{appid}__{name}.json`
     * Stored in the `./raw_metadata_dataset/` folder.
3. **Create Local Dataset**:

   * This dataset acts as a **sampling frame** for the next steps in the project (e.g., collecting patch notes).
   * Only metadata is retrieved at this point (no patch notes yet).


---

---

# Current Status and TODO

* ✅ Initial app ID list retrieved (257,148 entries total)
* ✅ Incremental filtering process implemented to extract game metadata
* ✅ Metadata stored in structured JSON files for local use
  * Aug 8, 2025: 27% of queries made

### 🛠️ TODO:

* Write a short update script to refresh the dataset with **new entries** without re-fetching the entire list.
* Begin defining sampling strategy for selecting games from the dataset for patch note analysis.

### 🤔 Related questions:
* 99% of games on Steam are indie games, but how much game time / size of user-base compared to AAA games?
* Can we use the raw game metadata to identify game clusters (PCA)?