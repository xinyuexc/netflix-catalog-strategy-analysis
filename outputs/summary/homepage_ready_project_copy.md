# Homepage-Ready Project Copy

## Short Summary

Netflix Catalog Strategy Analysis is a portfolio-grade data analysis project that treats the public Netflix titles metadata as a catalog strategy problem. Instead of a generic EDA notebook, the project builds normalized data tables, QA checks, reusable Python modules, staged notebooks, and business-facing outputs to analyze catalog mix, freshness, international expansion, audience positioning, concentration, and interpretable content segments.

## Methods Used

- data cleaning and QA checks
- normalization of multi-value fields into bridge tables
- feature engineering for freshness, lag, breadth, and country scope
- concentration and diversification metrics
- time-evolution analysis
- interpretable KMeans clustering
- cast and director ecosystem analysis with a constrained network view

## Strongest Findings

- The catalog is still movie-led, with Movies accounting for 68.4% of titles.
- The library is adult-skewed: Mature plus Teen titles represent 72.5% of the catalog.
- Supply is international but concentrated, with the top 3 countries accounting for 56.4% of country-tagged titles.
- TV inventory is noticeably fresher than movie inventory, suggesting different catalog roles.
- Geographic diversification expanded quickly in the late 2010s before stabilizing.
- The catalog can be summarized as a small set of strategic segments rather than one undifferentiated library.
- Recurring talent ecosystems add a differentiated view of how parts of the catalog are assembled.

## Limitations

- The dataset does not include viewership, watch time, retention, revenue, or popularity.
- Country tags are not exclusive production shares or market shares.
- `2020` is a partial snapshot year in the add-date timeline.
- Cast and director analysis depends on metadata completeness.
