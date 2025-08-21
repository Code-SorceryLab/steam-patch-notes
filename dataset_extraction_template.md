# 📊 Data Source Documentation Template

This template is intended to help researchers **systematically document** the process of selecting, accessing, and processing data sources in a study, with a focus on **transparency**, **reproducibility**, and **critical assessment**.

---

## 1. Project Overview

Briefly describe the **goal of your project**, the **type of analysis** to be conducted, and how the data source fits into the broader research objectives.

> *Example*:
> This project analyzes game patch notes to understand how digital games evolve over time. The dataset is built from publicly accessible data on a major distribution platform.

---

## 2. Data Source Selection

### 📌 Name and Description

* **Name of Data Source**:
* **Type** (e.g., platform, API, dataset):
* **Provider** (e.g., Valve Corporation, Kaggle, OpenStreetMap):
* **Access URL or Documentation**:

### Relevance for the Study

Describe **why this data source was selected** for the research.

* What kind of data does it provide?
* How does it align with the study’s research questions or objectives?

> *Example*:
> This source provides a unified access point to thousands of video games, which is essential for large-scale comparative analysis of patch notes.

### Representativeness

* How comprehensive or biased is the data source?
* Does it cover a specific domain, region, platform, or time period?
* Are there key entities or phenomena missing?

> *Example*:
> The platform hosts both AAA and indie games, offering a broad sample of the gaming industry, though console-exclusive titles are not included.

---

## 3. Data Access and Permissions

### Access Method

* **Method** (e.g., API, scraping, downloadable dataset):
* **Authentication or API keys required?**
* **Data format(s)** (e.g., JSON, CSV, HTML):

### Terms of Use

* **Terms of use link**:
* Are you permitted to use and store this data under the provider’s terms?
* Any special conditions for redistribution, publication, or modification?

---

## 4. Known Limitations and Mitigations

| Limitation                        | Description                         | Mitigation Strategy                                |
| --------------------------------- | ----------------------------------- | -------------------------------------------------- |
| Example: Rate Limit               | API allows 100,000 calls/day        | Schedule incremental queries over multiple days    |
| Example: Noisy Data               | Dataset contains non-target entries | Apply filtering rules and store only valid records |
| Example: Inconsistent Identifiers | AppIDs change based on endpoint     | Log and cross-check results to ensure consistency  |

Document any issues you encountered and how you addressed them to maintain **data integrity and completeness**.

---

## 5. Data Retrieval Process

### Tooling

* Scripts or notebooks used (e.g., Python script, Jupyter Notebook)
* Whether the script is one-time, periodic, or incremental
* Links towards existing tools if used

### Retrieval Workflow

1. **Initial Collection**:

   * Describe the first query (e.g., list of all IDs or entries).
   * Where is it stored? (e.g., `applist.json`)
2. **Filtering**:

   * Describe filtering logic to keep only relevant entries.
   * How are valid records identified?
3. **Storage**:

   * File format and structure (e.g., one JSON file per record).
   * Storage location (e.g., `./raw_metadata_dataset/`).

Use standards, preferably open, to store the dataset (e.g., json, csv)   
Define a license!!  
If the workflow has more than two steps, document it with a schema.

---

## 6. Dataset Summary

* **Number of records collected**:
* **% of data collected if incomplete**:
* **Fields/attributes included** (e.g., `appid`, `name`, `release_date`, etc.):
* **Size on disk**:
* **Structure** (e.g., flat files, database):

