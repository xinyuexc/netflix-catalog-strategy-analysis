# Netflix Catalog Strategy Analysis

## Project Objective

This repository frames the Netflix titles dataset as a catalog strategy problem, not a consumer behavior problem. The goal is to show portfolio-grade data analysis work that is structured, reproducible, commercially literate, and explicit about what the metadata can and cannot support.

Primary audience:
- hiring managers for business-facing Data Analyst, BI, and Strategy Analytics roles

Primary analytical lens:
- catalog composition
- content supply structure
- localization and international footprint
- catalog freshness and release-to-add lag
- audience positioning via maturity ratings
- concentration versus diversification

## Data Boundaries

This dataset supports metadata-based catalog analysis only. It does not support claims about performance outcomes such as watch time, viewership, retention, conversion, revenue, popularity, or recommendation effectiveness.

Every later insight in this project should respect three rules:
- stay descriptive or diagnostic unless an assumption is clearly labeled
- do not infer title performance from catalog presence
- do not imply causal business impact without outcome data

## Phase 1 Scope

Phase 1 establishes the analytical foundation:
- inspect schema quality and missingness
- preserve the raw file
- create normalized processed tables
- document cleaning decisions
- add QA outputs after major transformations
- create a reusable cleaning pipeline in `src/`

## Phase 1 Data Model

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
  - supporting parsed fields for `date_added`, `duration`, and rating harmonization

Bridge tables:
- `title_country`
- `title_genre`
- `title_cast`
- `title_director`

## Cleaning Plan

### Raw data handling
- Keep the original source file unchanged.
- Use `data/raw/netflix_titles.csv` as the canonical pipeline input for reproducible runs.

### Column standardization
- Validate that all expected source columns exist.
- Trim leading and trailing whitespace from string columns.
- Collapse repeated internal whitespace to reduce false duplicates.

### Date handling
- Parse `date_added` with the explicit format `%B %d, %Y` after trimming whitespace.
- Do not drop rows with missing `date_added`; keep missingness visible for QA and later metric design.

### Multi-value normalization
- Split comma-delimited values in `country`, `listed_in`, `cast`, and `director`.
- Store normalized entities in bridge tables rather than analyzing comma-separated strings.
- Remove duplicate `(show_id, entity)` pairs after exploding lists.

### Rating handling
- Preserve the raw `rating` column.
- Add:
  - `rating_system`
  - `rating_group`
  - `is_unrated`
- Treat `NR`, `UR`, and missing values as unknown or unrated.
- Keep rating group definitions broad and heuristic, because movie and TV systems are not perfectly equivalent.

### Duration handling
- Preserve the raw `duration` field.
- Parse it into `duration_value` and `duration_unit`.
- Standardize TV units to `season` and movie units to `min`.

## QA Outputs

Phase 1 should always materialize QA tables that answer:
- Are raw title rows preserved in the cleaned base table?
- Are `show_id` values still unique?
- How much missingness remains in the base table?
- Did date parsing fail beyond genuinely missing rows?
- Do bridge tables cover the same titles that have non-null source values?

## Next Analytical Steps

Phase 2 should build on these outputs to answer business-facing questions about:
- catalog composition by title type
- freshness and release-to-add lag
- geographic footprint and international breadth
- maturity rating positioning
- genre concentration and co-occurrence

