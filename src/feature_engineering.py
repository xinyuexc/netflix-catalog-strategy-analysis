"""Feature engineering helpers for the Phase 2 business analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROCESSED_TABLE_FILES = {
    "titles": "titles.csv",
    "title_country": "title_country.csv",
    "title_genre": "title_genre.csv",
    "title_cast": "title_cast.csv",
    "title_director": "title_director.csv",
}

COUNTRY_SCOPE_ORDER = ["Missing country", "Single-country", "Multi-country"]


def _coerce_numeric(series: pd.Series) -> pd.Series:
    """Convert numeric-looking columns back to nullable integers after CSV reloads."""
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def load_phase1_tables(data_directory: str | Path = "data/processed") -> dict[str, pd.DataFrame]:
    """Load the normalized Phase 1 outputs needed for Phase 2 analysis."""
    data_directory = Path(data_directory)
    tables = {
        "titles": pd.read_csv(data_directory / PROCESSED_TABLE_FILES["titles"], parse_dates=["date_added"]),
        "title_country": pd.read_csv(data_directory / PROCESSED_TABLE_FILES["title_country"]),
        "title_genre": pd.read_csv(data_directory / PROCESSED_TABLE_FILES["title_genre"]),
        "title_cast": pd.read_csv(data_directory / PROCESSED_TABLE_FILES["title_cast"]),
        "title_director": pd.read_csv(data_directory / PROCESSED_TABLE_FILES["title_director"]),
    }

    numeric_columns = ["release_year", "date_added_year", "date_added_month", "duration_value"]
    for column in numeric_columns:
        tables["titles"][column] = _coerce_numeric(tables["titles"][column])

    tables["titles"]["is_unrated"] = tables["titles"]["is_unrated"].astype(bool)
    return tables


def build_title_features(
    titles: pd.DataFrame,
    title_country: pd.DataFrame,
    title_genre: pd.DataFrame,
) -> pd.DataFrame:
    """Create a title-level feature table used across the business analysis notebook."""
    features = titles.copy()

    country_counts = title_country.groupby("show_id").size().rename("country_count")
    genre_counts = title_genre.groupby("show_id").size().rename("genre_count")

    features = features.join(country_counts, on="show_id").join(genre_counts, on="show_id")
    features["country_count"] = features["country_count"].fillna(0).astype(int)
    features["genre_count"] = features["genre_count"].fillna(0).astype(int)

    features["release_to_add_lag"] = features["date_added_year"] - features["release_year"]
    features["is_valid_release_to_add_lag"] = features["release_to_add_lag"].ge(0).fillna(False)
    features["release_to_add_lag_clean"] = features["release_to_add_lag"].where(
        features["is_valid_release_to_add_lag"]
    )

    features["country_scope"] = np.select(
        [
            features["country_count"].eq(0),
            features["country_count"].eq(1),
            features["country_count"].gt(1),
        ],
        COUNTRY_SCOPE_ORDER,
        default="Missing country",
    )
    features["country_scope"] = pd.Categorical(
        features["country_scope"], categories=COUNTRY_SCOPE_ORDER, ordered=True
    )

    for years in (1, 3, 5):
        features[f"is_recent_within_{years}y"] = (
            features["release_to_add_lag_clean"].le(years).fillna(False)
        )

    return features


def merge_titles_with_dimension(
    title_features: pd.DataFrame,
    bridge_table: pd.DataFrame,
    dimension_column: str,
) -> pd.DataFrame:
    """Join title-level features onto a normalized bridge table."""
    merged = bridge_table.drop_duplicates().merge(title_features, on="show_id", how="left")
    merged[dimension_column] = merged[dimension_column].astype("string")
    return merged


def build_country_view(title_features: pd.DataFrame, title_country: pd.DataFrame) -> pd.DataFrame:
    """Create the title-country analysis view."""
    return merge_titles_with_dimension(title_features, title_country, "country")


def build_genre_view(title_features: pd.DataFrame, title_genre: pd.DataFrame) -> pd.DataFrame:
    """Create the title-genre analysis view."""
    return merge_titles_with_dimension(title_features, title_genre, "genre")


def select_top_entities(
    bridge_table: pd.DataFrame,
    entity_column: str,
    id_column: str = "show_id",
    top_n: int = 10,
) -> list[str]:
    """Return the top entities ranked by distinct title coverage."""
    ranking = (
        bridge_table[[id_column, entity_column]]
        .drop_duplicates()
        .groupby(entity_column)[id_column]
        .nunique()
        .sort_values(ascending=False)
    )
    return ranking.head(top_n).index.tolist()
