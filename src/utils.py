"""Utility helpers used across the Netflix catalog strategy analysis project."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_SOURCE_COLUMNS = [
    "show_id",
    "type",
    "title",
    "director",
    "cast",
    "country",
    "date_added",
    "release_year",
    "rating",
    "duration",
    "listed_in",
    "description",
]

MULTIVALUE_COLUMN_MAP = {
    "country": "country",
    "listed_in": "genre",
    "cast": "cast_member",
    "director": "director",
}


def ensure_directory(path: str | Path) -> Path:
    """Create a directory when it does not exist and return it as a Path."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def validate_columns(
    df: pd.DataFrame,
    required_columns: list[str] | tuple[str, ...] = REQUIRED_SOURCE_COLUMNS,
) -> None:
    """Raise a clear error when required columns are missing."""
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def normalize_string_series(series: pd.Series) -> pd.Series:
    """Strip leading and trailing whitespace and collapse repeated spaces."""
    normalized = series.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    return normalized.mask(normalized.eq(""), pd.NA)


def split_and_explode_column(
    df: pd.DataFrame,
    id_column: str,
    source_column: str,
    value_column: str,
) -> pd.DataFrame:
    """Split comma-delimited fields into a normalized two-column bridge table."""
    working_column = "__split_value__"
    bridge = df[[id_column, source_column]].copy()
    bridge[source_column] = normalize_string_series(bridge[source_column])
    bridge = bridge.dropna(subset=[source_column])
    bridge[source_column] = bridge[source_column].str.split(r"\s*,\s*")
    bridge = bridge.explode(source_column, ignore_index=True)
    bridge[working_column] = normalize_string_series(bridge[source_column])
    bridge = bridge.drop(columns=[source_column]).dropna(subset=[working_column])
    bridge = bridge.rename(columns={working_column: value_column})
    bridge = bridge.drop_duplicates().sort_values([id_column, value_column]).reset_index(drop=True)
    return bridge


def save_dataframe(df: pd.DataFrame, output_path: str | Path) -> None:
    """Save a DataFrame as CSV using UTF-8 encoding."""
    output_path = Path(output_path)
    ensure_directory(output_path.parent)
    df.to_csv(output_path, index=False)


def share(series: pd.Series) -> pd.Series:
    """Return normalized value counts as a share series."""
    counts = series.value_counts(dropna=False)
    return counts / counts.sum()
