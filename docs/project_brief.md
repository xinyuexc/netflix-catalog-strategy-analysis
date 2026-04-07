# Netflix Catalog Strategy Analysis

## Project Purpose

This repository turns the public Netflix titles metadata into a **catalog strategy** case study. The project is built for portfolio presentation and is intended to demonstrate structured, business-facing data analysis rather than casual exploration.

Primary audience:
- hiring managers for Data Analyst, BI, Strategy Analytics, and Analytics Engineering roles

Primary objective:
- show strong analytical judgment through reproducible data modeling, scoped interpretation, interpretable metrics, and concise communication

## Source Materials

- Canonical raw dataset: `data/raw/netflix_titles.csv`
- Archived starter notebook: `data/raw/netflix-data-analysis.ipynb`
- Source page for both: <https://www.kaggle.com/code/chirag9073/netflix-data-analysis/input>

The Kaggle page above provided the raw file and an initial notebook. This repository restructures that starting point into a staged analytics project with cleaning pipelines, normalized tables, QA outputs, modular code, and portfolio-ready executive packaging.

## Analytical Framing

The project is designed to answer questions such as:

- How is the catalog split between Movies and TV Shows?
- Which genres, ratings, and countries dominate the library?
- How fresh is the catalog, and how long after release are titles added?
- How international is the catalog, and how concentrated is supply?
- What does the maturity mix imply about audience positioning?
- Can the catalog be summarized as a small number of interpretable strategic segments?
- Do recurring cast and director ecosystems reveal meaningful catalog niches?

## Data Boundaries

This dataset supports **catalog metadata analysis only**.

It supports:
- catalog composition
- content mix and portfolio structure
- geography and international footprint
- freshness and release-to-add lag
- rating and audience-positioning analysis
- concentration and diversification analysis
- interpretable title segmentation
- repeated people and ecosystem analysis

It does **not** support:
- viewership
- watch time
- retention
- revenue
- popularity
- conversion
- recommendation performance

Project rule:
- do not imply performance, causal business impact, or title success from catalog metadata alone

## Repository Design Principles

- preserve raw inputs
- normalize multi-value fields into bridge tables
- keep reusable logic in `src/`
- add QA outputs after major transformations
- separate engineering, analysis, and packaging into staged notebooks
- prefer interpretable business analysis over decorative techniques

## Phase Structure

### Phase 1 — Foundations

Goal:
- build a reproducible analytical base

Deliverables:
- repo scaffold
- cleaning pipeline in `src/cleaning.py`
- utility functions in `src/utils.py`
- normalized processed tables
- QA outputs in `data/processed/`
- `01_data_audit.ipynb`

Core outputs:
- `titles`
- `title_country`
- `title_genre`
- `title_cast`
- `title_director`

### Phase 2 — Core Business Analysis

Goal:
- answer the main business-facing catalog questions

Deliverables:
- `02_feature_engineering.ipynb`
- `03_business_analysis.ipynb`
- metrics and charting helpers in `src/feature_engineering.py`, `src/metrics.py`, and `src/visualization.py`
- tables and figures under `outputs/`

Analytical modules:
- catalog composition
- freshness and release lag
- geographic footprint
- audience positioning
- genre concentration and co-occurrence

### Phase 3 — Advanced Analysis

Goal:
- deepen the project beyond standard slicing without losing interpretability

Deliverables:
- `04_segmentation_networks.ipynb`
- time-evolution analysis
- interpretable title clustering
- people ecosystem analysis

Advanced modules:
- titles added over time
- mix change over time
- geographic diversification over time
- business-readable title segments
- recurring cast and director ecosystems

### Phase 4 — Packaging

Goal:
- turn the project into a concise, public portfolio asset

Deliverables:
- `05_executive_summary.ipynb`
- concise root `README.md`
- final executive findings table
- final public figure shortlist
- homepage-ready project copy

Packaging standard:
- readable in a few minutes
- business-facing rather than academic
- explicit about data limitations

## Data Model

Base table:
- `titles`
  - `show_id`
  - `title`
  - `type`
  - `release_year`
  - `date_added`
  - `rating`
  - `duration`
  - `description`
  - derived parsed fields for duration, add date, and rating harmonization

Bridge tables:
- `title_country`
- `title_genre`
- `title_cast`
- `title_director`

## Key Methods

- schema auditing
- missingness review
- explicit date parsing
- string normalization
- bridge-table normalization
- freshness and lag metrics
- concentration curves and HHI-style measures
- mix and co-occurrence analysis
- interpretable KMeans clustering
- constrained network analysis for people ecosystems

## Final Public Storyline

The finished project should communicate five ideas clearly:

- Netflix’s catalog is movie-led but strategically layered
- freshness differs across content types and catalog buckets
- international breadth increased materially, but concentration remains important
- the library can be summarized as a few strategic segments
- recurring creative ecosystems add differentiated depth to the analysis

## Final Deliverable Standard

A strong final version of this project should feel:
- polished
- structured
- reproducible
- commercially literate
- honest about limitations

It should **not** feel like:
- a generic Kaggle notebook
- an academic methods demo
- an over-visualized dashboard with weak interpretation
