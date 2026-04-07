"""Metric helpers for portfolio mix, freshness, and concentration analysis."""

from __future__ import annotations

import pandas as pd


def share_table(df: pd.DataFrame, column: str, top_n: int | None = None) -> pd.DataFrame:
    """Return counts and shares for a categorical field."""
    summary = (
        df[column]
        .fillna("Missing")
        .value_counts(dropna=False)
        .rename_axis(column)
        .reset_index(name="title_count")
    )
    summary["share"] = summary["title_count"] / summary["title_count"].sum()
    if top_n is not None:
        summary = summary.head(top_n).copy()
    return summary

