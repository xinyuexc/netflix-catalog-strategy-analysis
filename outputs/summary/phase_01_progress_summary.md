# Phase 1 Progress Summary

## Completed

- Audited the raw Netflix titles dataset schema and missingness profile.
- Created a professional project scaffold with `data/`, `docs/`, `notebooks/`, `outputs/`, and `src/`.
- Implemented the Phase 1 cleaning pipeline and reusable utility helpers.
- Normalized multi-value fields into bridge tables for countries, genres, cast, and directors.
- Saved processed tables and QA outputs under `data/processed/`.
- Created and executed `notebooks/01_data_audit.ipynb`.

## Key Assumptions

- `show_id` is treated as an identifier, not a numeric measure.
- `date_added` should be parsed with the explicit format `%B %d, %Y` after trimming whitespace.
- `NR`, `UR`, and missing `rating` values are grouped as unknown or unrated.
- `rating_group` is a broad portfolio-facing heuristic, not a strict regulatory equivalence.

## Data Limitations Found

- `director` is missing for 1,969 titles.
- `cast` is missing for 570 titles.
- `country` is missing for 476 titles.
- `date_added` is missing for 11 titles.
- `rating` is missing for 10 titles.

## Next Step

Phase 2 should use the cleaned base table and bridge tables to build the metric dictionary and answer the first business-facing questions:
- catalog composition by type
- freshness and release-to-add lag
- geographic footprint
- maturity rating positioning
- genre concentration and co-occurrence
