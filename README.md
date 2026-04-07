# Netflix Catalog Strategy Analysis

Portfolio-grade analytics case study that reframes the public Netflix titles metadata as a **catalog strategy** problem rather than a casual EDA notebook. The project uses reproducible cleaning pipelines, normalized bridge tables, QA checks, staged notebooks, and interpretable advanced analysis to explain how the catalog is structured, how it evolved, and which patterns look strategically meaningful.

## Project Positioning

This project is designed to answer business-facing questions such as:

- How movie-led versus TV-led is the catalog?
- How fresh is the library, and how quickly are titles added after release?
- How international is the footprint, and how concentrated is supply?
- What does the rating mix suggest about audience positioning?
- Which content segments and creative ecosystems appear repeatedly?

The dataset supports catalog structure analysis. It does **not** support claims about viewership, retention, revenue, popularity, or title performance.

## Executive Takeaways

- Movies are 68.4% of titles, so the catalog is still movie-led in volume.
- Mature plus Teen titles account for 72.5% of the library, indicating an adult-skewed positioning.
- Country supply is broad but concentrated: the top 3 countries account for 56.4% of country-tagged titles, and the top 10 account for 76.5%.
- TV inventory is materially fresher than Movies: 80.3% of TV Shows were added within 3 years of release versus 64.6% for Movies.
- Geographic diversification accelerated sharply in the late 2010s, rising from 16 represented countries in 2015 to 82 in 2018 before later stabilizing.
- The catalog is more interpretable as a small set of strategic segments than as one undifferentiated library.
- Recurring cast ecosystems suggest that parts of the catalog are built around repeatable creative communities rather than isolated titles.

## What Makes This Repo Portfolio-Grade

- Raw data is preserved and cleaned outputs are documented.
- Multi-value columns are normalized into bridge tables instead of analyzed as comma-separated strings.
- Reusable logic lives in `src/` rather than being trapped in notebooks.
- Each stage is separated into an audit, feature layer, business analysis, advanced analysis, and executive summary.

## Data Source and Attribution

- Raw file: `data/raw/netflix_titles.csv`
- Archived starter notebook: `data/raw/netflix-data-analysis.ipynb`
- Source page for both the raw dataset and starter notebook: <https://www.kaggle.com/code/chirag9073/netflix-data-analysis/input>

The raw dataset and the starter notebook in `data/raw/` were sourced from that Kaggle page. This repository then restructures the starting materials into a reproducible analytics project with cleaning pipelines, normalized tables, QA outputs, business-facing interpretation, and portfolio packaging.

## Notebook Map

- `01_data_audit.ipynb`: source schema review, missingness, parse quality, and QA checks
- `02_feature_engineering.ipynb`: title-level analytical layer built from normalized tables
- `03_business_analysis.ipynb`: catalog mix, freshness, geography, audience positioning, and genre relationships
- `04_segmentation_networks.ipynb`: time evolution, interpretable clustering, and people ecosystems
- `05_executive_summary.ipynb`: final summary for business readers and public portfolio packaging

## Repository Structure

```text
netflix-catalog-strategy-analysis/
├─ data/
│  ├─ raw/
│  │  ├─ netflix_titles.csv
│  │  └─ netflix-data-analysis.ipynb
│  └─ processed/
├─ notebooks/
├─ src/
├─ outputs/
│  ├─ figures/
│  ├─ tables/
│  └─ summary/
├─ docs/
│  └─ project_brief.md
├─ requirements.txt
└─ README.md
```

## Reproduce the Project

```bash
pip install -r requirements.txt
python -m src.cleaning --input data/raw/netflix_titles.csv --output data/processed
```

Then run notebooks `01` through `05` in order.

## Project Documents

- `docs/project_brief.md`: full-project brief covering scope, data boundaries, phase plan, methods, and portfolio packaging
- `data/raw/netflix-data-analysis.ipynb`: archived starter notebook retained for provenance only, not as the main analytical workflow

## Strongest Public Outputs

- `outputs/figures/phase2_03_genre_mix_by_type.png`
- `outputs/figures/phase2_04_concentration_curves.png`
- `outputs/figures/phase2_06_release_to_add_lag_by_type.png`
- `outputs/figures/phase3_01_titles_added_profile.png`
- `outputs/figures/phase3_05_geographic_diversification_over_time.png`
- `outputs/figures/phase3_07_cluster_profile_heatmap.png`
- `outputs/figures/phase3_08_cast_ecosystem_network.png`

## Limits

- Metadata only: no outcomes, demand, or performance signals
- Country tags are not exclusive market shares
- `date_added_year = 2020` is a partial snapshot year
- Cast and director analysis depends on credit completeness
