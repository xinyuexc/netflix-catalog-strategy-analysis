# Phase 2 Progress Summary

## Completed

- Extended the reusable analysis layer in `src/` for Phase 2 feature engineering, metrics, and visualization.
- Built the main business analysis notebook at `notebooks/03_business_analysis.ipynb`.
- Executed the notebook end to end and materialized Phase 2 outputs.
- Saved 23 analysis tables to `outputs/tables/`.
- Saved 11 polished figures to `outputs/figures/`.

## Key Design Decisions

- Reused Phase 1 normalized tables instead of re-parsing raw metadata.
- Treated negative release-to-add lag values as metadata anomalies and excluded 9 such titles from lag metrics.
- Used harmonized `rating_group` buckets for business interpretation while preserving the raw rating field in the underlying processed data.
- Measured concentration with cumulative share curves and HHI-style summaries rather than weak share-only charts.
- Used genre pair lift to support interpretable co-occurrence analysis instead of jumping directly to black-box clustering.

## Main Findings

- The catalog is movie-led in volume, but TV behaves like a more curated strategic layer.
- The catalog is strongly mature- and teen-skewed overall.
- Country breadth exists, but the production footprint is concentrated in a small core led by the United States, India, and the United Kingdom.
- Freshness is strongest in TV-led and international-expansion segments.
- Genre co-occurrence reveals coherent bundle structures rather than flat, interchangeable tagging.

## Data Limitations

- Country totals reflect title-country tags and are not mutually exclusive shares.
- `date_added_year = 2021` is snapshot-limited because the current dataset runs through September 25, 2021, so it should not be treated as a full-year trend.
- Missing country metadata is materially higher for TV Shows than for Movies.
- The dataset supports catalog structure, not content performance.

## Next Step

Phase 3 should focus on interpretable segmentation and network analysis:
- title clustering using engineered title-level features
- creator and cast network structure
- business-labeled catalog segments rather than generic unsupervised output
