# Netflix Catalog Strategy Analysis

A business-oriented analytics case study that reframes the public Netflix titles metadata as a **catalog strategy** problem rather than a generic EDA exercise.

This project uses reproducible cleaning pipelines, normalized bridge tables, QA checks, staged notebooks, and interpretable advanced analysis to answer a simple question: **what does the Netflix catalog look like structurally, how did it evolve, and which patterns are strategically meaningful?**

## What this project answers

This repository focuses on questions such as:

- How movie-led versus TV-led is the catalog?
- How fresh is the library, and how quickly are titles added after release?
- How international is the footprint, and how concentrated is supply?
- What does the rating mix suggest about audience positioning?
- Which content segments and creative ecosystems recur across the catalog?

This dataset supports **catalog structure analysis**. It does **not** support claims about viewership, retention, revenue, popularity, or title performance.

## Key findings

- Movies account for **68.4%** of titles, so the catalog remains movie-led in volume.
- Mature + Teen titles make up **72.5%** of the library, indicating adult-skewed positioning.
- Country supply is broad but concentrated: the top 3 countries account for **56.4%** of country-tagged titles, and the top 10 account for **76.5%**.
- TV inventory is materially fresher than Movies: **80.3%** of TV Shows were added within 3 years of release versus **64.6%** for Movies.
- Geographic diversification expanded rapidly in the late 2010s before stabilizing.
- The catalog is easier to interpret as a small set of strategic segments than as one undifferentiated library.
- Recurring cast ecosystems suggest that parts of the catalog are built around repeatable creative communities rather than isolated titles.

## Repository guide

### Notebooks

- [`01_data_audit.ipynb`](notebooks/01_data_audit.ipynb) — schema review, missingness, parse quality, and QA checks
- [`02_feature_engineering.ipynb`](notebooks/02_feature_engineering.ipynb) — title-level analytical layer built from normalized tables
- [`03_business_analysis.ipynb`](notebooks/03_business_analysis.ipynb) — catalog mix, freshness, geography, audience positioning, and genre relationships
- [`04_segmentation_networks.ipynb`](notebooks/04_segmentation_networks.ipynb) — time evolution, interpretable clustering, and people ecosystems
- [`05_executive_summary.ipynb`](notebooks/05_executive_summary.ipynb) — final summary for business readers and public portfolio packaging

### Data Source

- Raw data: [`netflix_titles.csv`](data/raw/netflix_titles.csv) [Source](https://www.kaggle.com/datasets/shivamb/netflix-shows)
- Archived starter notebook: [`netflix-data-analysis.ipynb`](data/raw/netflix-data-analysis.ipynb) [Source](https://www.kaggle.com/code/chirag9073/netflix-data-analysis/notebook)

The raw dataset and the initial exploratory notebook in this repo were sourced from that Kaggle page. This repository then restructures the work into a reproducible analytics project with cleaning pipelines, normalized tables, QA outputs, business-facing interpretation, and portfolio packaging.

## Reproduce the Project

```bash
pip install -r requirements.txt
python -m src.cleaning --input data/raw/netflix_titles.csv --output data/processed
```
Then run notebooks `01` through `05` in order.

## Strongest Outputs

- [`genre_mix_by_type.png`](outputs/figures/phase2_03_genre_mix_by_type.png)
- [`concentration_curves.png`](outputs/figures/phase2_04_concentration_curves.png)
- [`release_to_add_lag_by_type.png`](outputs/figures/phase2_06_release_to_add_lag_by_type.png)
- [`titles_added_profile.png`](outputs/figures/phase3_01_titles_added_profile.png)
- [`geographic_diversification_over_time.png`](outputs/figures/phase3_05_geographic_diversification_over_time.png)
- [`cluster_profile_heatmap.png`](outputs/figures/phase3_07_cluster_profile_heatmap.png)
- [`cast_ecosystem_network.png`](outputs/figures/phase3_08_cast_ecosystem_network.png)


## Limits

- Metadata only: no outcomes, demand, or performance signals
- Country tags are not exclusive market shares
- `date_added_year = 2021` is a partial snapshot year because the data currently runs through September 25, 2021
- Cast and director analysis depends on credit completeness
