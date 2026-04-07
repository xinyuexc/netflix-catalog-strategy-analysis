# Netflix Catalog Strategy Analysis

A portfolio-grade, business-oriented data analysis project built from the Netflix titles dataset. The repository is designed to demonstrate structured analytics work: reproducible pipelines, normalized tables, QA outputs, and staged notebooks instead of a single exploratory notebook.

## Business Framing

This project uses Netflix catalog metadata to study:
- catalog composition
- movie versus TV portfolio mix
- localization versus globalization patterns
- freshness and release-to-add lag
- maturity rating positioning
- concentration versus diversification

The dataset does not contain watch time, viewership, retention, revenue, conversion, or popularity data, so this project does not make performance claims.

## Phase 1 Outputs

Phase 1 establishes the foundation for later business analysis:
- canonical raw input in `data/raw/netflix_titles.csv`
- reusable cleaning pipeline in `src/cleaning.py`
- normalized bridge tables for countries, genres, cast, and directors
- QA outputs saved to `data/processed/`
- audit notebook in `notebooks/01_data_audit.ipynb`
- written project brief in `docs/project_brief.md`

## Repository Layout

```text
netflix-catalog-strategy-analysis/
├─ README.md
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ external/
├─ notebooks/
├─ src/
├─ outputs/
│  ├─ tables/
│  ├─ figures/
│  └─ summary/
├─ docs/
├─ requirements.txt
└─ .gitignore
```

## Processed Tables

Saved under `data/processed/`:
- `titles.csv`
- `title_country.csv`
- `title_genre.csv`
- `title_cast.csv`
- `title_director.csv`
- `qa_table_counts.csv`
- `qa_titles_missingness.csv`
- `qa_bridge_coverage.csv`
- `qa_parse_checks.csv`

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Phase 1 cleaning pipeline:

```bash
python -m src.cleaning --input data/raw/netflix_titles.csv --output data/processed
```

## Documentation

- Project brief: `docs/project_brief.md`
- Audit notebook: `notebooks/01_data_audit.ipynb`
- Legacy exploratory notebook retained for reference: `netflix-data-analysis.ipynb`
