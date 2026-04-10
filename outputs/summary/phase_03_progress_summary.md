# Phase 03 Progress Summary

## Completed work

- Built and executed [04_segmentation_networks.ipynb](/Users/xinyue/Documents/projects/netflix_da/notebooks/04_segmentation_networks.ipynb)
- Added reusable Phase 3 helpers in:
  - [feature_engineering.py](/Users/xinyue/Documents/projects/netflix_da/src/feature_engineering.py)
  - [metrics.py](/Users/xinyue/Documents/projects/netflix_da/src/metrics.py)
  - [visualization.py](/Users/xinyue/Documents/projects/netflix_da/src/visualization.py)
  - [utils.py](/Users/xinyue/Documents/projects/netflix_da/src/utils.py)
- Saved 8 Phase 3 figures under [outputs/figures](/Users/xinyue/Documents/projects/netflix_da/outputs/figures)
- Saved Phase 3 analysis tables under [outputs/tables](/Users/xinyue/Documents/projects/netflix_da/outputs/tables)
- Added clustering dependencies to [requirements.txt](/Users/xinyue/Documents/projects/netflix_da/requirements.txt)

## What Phase 3 adds

- Time evolution: the catalog is now analyzed as a changing portfolio rather than a static snapshot.
- Interpretable segmentation: titles are grouped into six business-readable segments rather than treated as one undifferentiated library.
- People ecosystems: repeated cast and director patterns are translated into reusable sourcing and ecosystem narratives.

## Key design decisions

- Time evolution is tracked on `date_added_year` rather than raw release year because the strategic question is how the catalog was assembled over time.
- Clustering uses a small, interpretable feature set: type, rating group, release year, release-to-add lag, country breadth, genre breadth, recency, and top-genre flags.
- `k = 6` was selected because it gave the strongest silhouette among tested options while preserving business-readable segment definitions.
- Network analysis is intentionally constrained to one main cast ecosystem graph plus supporting tables. This keeps the output commercially interpretable instead of academically overloaded.
- Cluster profiles are calculated as title coverage within cluster rather than tag-volume share, which avoids overstating heavily multi-tagged titles.

## Data limitations discovered

- `date_added_year = 2021` is the partial snapshot year in the refreshed dataset and should not be read as a full-year trend endpoint.
- Country-based time evolution still reflects country tags, not exclusive production ownership or market share.
- People analysis is limited by credit completeness in `cast` and `director`; missing credits reduce network coverage.
- Repeated presence in the catalog does not imply audience demand, strategic success, or economic value.

## Strong outputs worth keeping

- `phase3_01_titles_added_profile.png`
- `phase3_05_geographic_diversification_over_time.png`
- `phase3_06_cluster_size_summary.png`
- `phase3_07_cluster_profile_heatmap.png`
- `phase3_08_cast_ecosystem_network.png`

## Outputs to demote or keep in appendix

- `phase3_director_cast_collaborations.csv`
- full node-level network exports
- large cluster assignment tables

These are useful for auditability, but they are weaker as front-page portfolio artifacts.

## Recommended next step

Phase 4 should focus on packaging:

- build `05_executive_summary.ipynb`
- narrow the project to the strongest cross-phase visuals
- rewrite the README into a concise portfolio narrative
- frame the deliverable around catalog strategy, localization, freshness, concentration, and interpretable portfolio segments
