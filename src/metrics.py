"""Metric helpers for Phase 2 business analysis."""

from __future__ import annotations

from itertools import combinations

import pandas as pd


def _deduplicate_for_counts(
    df: pd.DataFrame,
    group_columns: list[str],
    id_column: str,
) -> pd.DataFrame:
    """Drop duplicate entity-title pairs before aggregation."""
    return df[group_columns + [id_column]].drop_duplicates()


def herfindahl_index(shares: pd.Series) -> float:
    """Compute a simple concentration score from category shares."""
    return float((shares.pow(2)).sum())


def share_table(
    df: pd.DataFrame,
    column: str,
    id_column: str = "show_id",
    top_n: int | None = None,
    missing_label: str = "Missing",
) -> pd.DataFrame:
    """Return counts, shares, and cumulative shares for one categorical field."""
    working = df[[id_column, column]].drop_duplicates().copy()
    working[column] = working[column].astype("string").fillna(missing_label)

    summary = (
        working.groupby(column)[id_column]
        .nunique()
        .sort_values(ascending=False)
        .rename("title_count")
        .reset_index()
    )
    summary["share"] = summary["title_count"] / summary["title_count"].sum()
    summary["cumulative_share"] = summary["share"].cumsum()
    summary["entity_rank"] = range(1, len(summary) + 1)
    summary["hhi"] = herfindahl_index(summary["share"])

    if top_n is not None:
        summary = summary.head(top_n).copy()
    return summary


def distribution_table(
    df: pd.DataFrame,
    column: str,
    id_column: str = "show_id",
) -> pd.DataFrame:
    """Return a count distribution sorted by the column value."""
    working = df[[id_column, column]].drop_duplicates().dropna(subset=[column])
    distribution = (
        working.groupby(column)[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
        .sort_values(column)
        .reset_index(drop=True)
    )
    return distribution


def mix_table(
    df: pd.DataFrame,
    group_column: str,
    category_column: str,
    id_column: str = "show_id",
    missing_label: str = "Missing",
    top_n_categories: int | None = None,
) -> pd.DataFrame:
    """Return a grouped mix table with within-group shares."""
    working = _deduplicate_for_counts(df, [group_column, category_column], id_column).copy()
    working[group_column] = working[group_column].astype("string").fillna(missing_label)
    working[category_column] = working[category_column].astype("string").fillna(missing_label)

    if top_n_categories is not None:
        top_categories = (
            working.groupby(category_column)[id_column]
            .nunique()
            .sort_values(ascending=False)
            .head(top_n_categories)
            .index
        )
        working = working[working[category_column].isin(top_categories)].copy()

    summary = (
        working.groupby([group_column, category_column])[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
    )
    summary["group_total"] = summary.groupby(group_column)["title_count"].transform("sum")
    summary["share_within_group"] = summary["title_count"] / summary["group_total"]
    summary["rank_within_group"] = (
        summary.groupby(group_column)["title_count"].rank(method="first", ascending=False).astype(int)
    )
    return summary.sort_values([group_column, "title_count"], ascending=[True, False]).reset_index(drop=True)


def concentration_curve(
    df: pd.DataFrame,
    column: str,
    id_column: str = "show_id",
) -> pd.DataFrame:
    """Return the ranked cumulative-share curve for one entity set."""
    summary = share_table(df, column, id_column=id_column)
    return summary[[column, "title_count", "share", "cumulative_share", "entity_rank", "hhi"]].copy()


def concentration_summary(
    df: pd.DataFrame,
    column: str,
    id_column: str = "show_id",
) -> pd.DataFrame:
    """Return a compact concentration summary for one categorical dimension."""
    curve = concentration_curve(df, column, id_column=id_column)
    shares = curve["share"]
    summary = pd.DataFrame(
        [
            {
                "dimension": column,
                "entity_count": int(curve[column].nunique()),
                "top_3_share": float(shares.head(3).sum()),
                "top_5_share": float(shares.head(5).sum()),
                "top_10_share": float(shares.head(10).sum()),
                "entities_to_50pct": int((curve["cumulative_share"] < 0.5).sum() + 1),
                "hhi": float(curve["hhi"].iloc[0]),
            }
        ]
    )
    return summary


def freshness_summary(
    df: pd.DataFrame,
    group_column: str,
    id_column: str = "show_id",
    lag_column: str = "release_to_add_lag_clean",
    release_year_column: str = "release_year",
) -> pd.DataFrame:
    """Return freshness and release-lag metrics for a grouping dimension."""
    working = df[[id_column, group_column, lag_column, release_year_column]].drop_duplicates().copy()
    working = working.dropna(subset=[group_column])

    summary = working.groupby(group_column).agg(
        title_count=(id_column, "nunique"),
        valid_lag_title_count=(lag_column, lambda s: s.notna().sum()),
        median_release_year=(release_year_column, "median"),
        median_lag=(lag_column, "median"),
        p75_lag=(lag_column, lambda s: s.quantile(0.75)),
        share_recent_1y=(lag_column, lambda s: s.le(1).mean()),
        share_recent_3y=(lag_column, lambda s: s.le(3).mean()),
        share_recent_5y=(lag_column, lambda s: s.le(5).mean()),
    )
    summary = summary.reset_index().sort_values("title_count", ascending=False).reset_index(drop=True)
    return summary


def country_scope_summary(
    title_features: pd.DataFrame,
    group_column: str = "type",
    id_column: str = "show_id",
) -> pd.DataFrame:
    """Summarize missing, single-country, and multi-country title shares by group."""
    working = title_features[[id_column, group_column, "country_scope"]].drop_duplicates().copy()
    summary = (
        working.groupby([group_column, "country_scope"], observed=False)[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
    )
    summary["group_total"] = summary.groupby(group_column)["title_count"].transform("sum")
    summary["share_within_group"] = summary["title_count"] / summary["group_total"]
    return summary.sort_values([group_column, "country_scope"]).reset_index(drop=True)


def top_entities_over_time(
    df: pd.DataFrame,
    entity_column: str,
    year_column: str = "date_added_year",
    id_column: str = "show_id",
    top_n: int = 5,
) -> pd.DataFrame:
    """Track the top entities over the `year_column` timeline."""
    working = _deduplicate_for_counts(df.dropna(subset=[year_column]), [entity_column, year_column], id_column)

    top_entities = (
        working.groupby(entity_column)[id_column]
        .nunique()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )

    timeline = (
        working[working[entity_column].isin(top_entities)]
        .groupby([year_column, entity_column])[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
    )
    timeline["year_total"] = timeline.groupby(year_column)["title_count"].transform("sum")
    timeline["share_within_selected_entities"] = timeline["title_count"] / timeline["year_total"]
    return timeline.sort_values([year_column, "title_count"], ascending=[True, False]).reset_index(drop=True)


def pair_lift_table(
    bridge_table: pd.DataFrame,
    entity_column: str,
    id_column: str = "show_id",
    top_n: int = 12,
) -> pd.DataFrame:
    """Compute observed versus expected co-occurrence lift for the top entities."""
    deduped = bridge_table[[id_column, entity_column]].drop_duplicates().copy()
    top_entities = (
        deduped.groupby(entity_column)[id_column]
        .nunique()
        .sort_values(ascending=False)
        .head(top_n)
        .index
        .tolist()
    )

    filtered = deduped[deduped[entity_column].isin(top_entities)].copy()
    title_sets = (
        filtered.groupby(id_column)[entity_column]
        .apply(lambda values: sorted(set(values)))
        .tolist()
    )

    observed_pairs: dict[tuple[str, str], int] = {
        pair: 0 for pair in combinations(sorted(top_entities), 2)
    }
    for entity_list in title_sets:
        for pair in combinations(entity_list, 2):
            observed_pairs[tuple(sorted(pair))] += 1

    entity_counts = (
        filtered.groupby(entity_column)[id_column]
        .nunique()
        .rename("entity_title_count")
        .to_dict()
    )
    total_titles = deduped[id_column].nunique()

    rows = []
    for (entity_a, entity_b), pair_count in observed_pairs.items():
        expected_count = (entity_counts[entity_a] * entity_counts[entity_b]) / total_titles
        lift = pair_count / expected_count if expected_count else pd.NA
        rows.append(
            {
                "entity_a": entity_a,
                "entity_b": entity_b,
                "pair_count": pair_count,
                "expected_count": expected_count,
                "lift": lift,
                "pair_share_of_titles": pair_count / total_titles,
                "entity_a_title_count": entity_counts[entity_a],
                "entity_b_title_count": entity_counts[entity_b],
            }
        )

    pairs = pd.DataFrame(rows)
    return pairs.sort_values(["lift", "pair_count"], ascending=[False, False]).reset_index(drop=True)


def matrix_from_mix(
    mix_df: pd.DataFrame,
    index_column: str,
    column_column: str,
    value_column: str = "share_within_group",
) -> pd.DataFrame:
    """Pivot a mix table into a heatmap-ready matrix."""
    matrix = mix_df.pivot(index=index_column, columns=column_column, values=value_column).fillna(0.0)
    return matrix
