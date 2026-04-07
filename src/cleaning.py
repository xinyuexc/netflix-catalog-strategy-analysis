"""Cleaning pipeline for the Netflix catalog strategy analysis project."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.utils import (
    MULTIVALUE_COLUMN_MAP,
    REQUIRED_SOURCE_COLUMNS,
    ensure_directory,
    normalize_string_series,
    save_dataframe,
    split_and_explode_column,
    validate_columns,
)

MOVIE_RATINGS = {"G", "PG", "PG-13", "R", "NC-17"}
TV_RATINGS = {"TV-Y", "TV-Y7", "TV-Y7-FV", "TV-G", "TV-PG", "TV-14", "TV-MA"}
UNRATED_VALUES = {"NR", "UR"}

TITLES_OUTPUT_COLUMNS = [
    "show_id",
    "title",
    "type",
    "release_year",
    "date_added",
    "date_added_year",
    "date_added_month",
    "rating",
    "rating_system",
    "rating_group",
    "is_unrated",
    "duration",
    "duration_value",
    "duration_unit",
    "description",
]


def read_raw_titles(csv_path: str | Path) -> pd.DataFrame:
    """Read the raw titles file while preserving identifiers as strings."""
    dataframe = pd.read_csv(csv_path, dtype={"show_id": "string"})
    validate_columns(dataframe, REQUIRED_SOURCE_COLUMNS)
    return dataframe


def infer_rating_system(rating: str | pd.NA) -> str:
    """Classify ratings into broad systems for later portfolio analysis."""
    if pd.isna(rating):
        return "Unknown / Unrated"
    if rating in TV_RATINGS:
        return "TV Parental Guidelines"
    if rating in MOVIE_RATINGS:
        return "MPAA-like"
    if rating in UNRATED_VALUES:
        return "Unknown / Unrated"
    return "Other"


def infer_rating_group(rating: str | pd.NA) -> str:
    """Map detailed ratings to broad, interpretable audience buckets."""
    if pd.isna(rating) or rating in UNRATED_VALUES:
        return "Unknown / Unrated"
    if rating in {"TV-Y", "TV-Y7", "TV-Y7-FV"}:
        return "Kids"
    if rating in {"TV-G", "G", "TV-PG", "PG"}:
        return "Family"
    if rating in {"TV-14", "PG-13"}:
        return "Teen"
    if rating in {"TV-MA", "R", "NC-17"}:
        return "Mature"
    return "Other"


def parse_date_added(series: pd.Series) -> pd.Series:
    """Parse date_added using the dataset's month-day-year string format."""
    return pd.to_datetime(normalize_string_series(series), format="%B %d, %Y", errors="coerce")


def parse_duration_parts(series: pd.Series) -> pd.DataFrame:
    """Split the duration field into numeric value and standardized unit."""
    extracted = normalize_string_series(series).str.extract(
        r"^(?P<duration_value>\d+)\s+(?P<duration_unit>min|Season|Seasons)$"
    )
    extracted["duration_value"] = pd.to_numeric(
        extracted["duration_value"], errors="coerce"
    ).astype("Int64")
    extracted["duration_unit"] = extracted["duration_unit"].replace(
        {"Season": "season", "Seasons": "season", "min": "min"}
    )
    extracted["duration_unit"] = extracted["duration_unit"].astype("string")
    return extracted


def standardize_titles_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Apply column-level cleaning rules without removing source rows."""
    validate_columns(df, REQUIRED_SOURCE_COLUMNS)
    cleaned = df.copy()

    object_columns = cleaned.select_dtypes(include=["object", "string"]).columns
    for column in object_columns:
        if column == "date_added":
            continue
        cleaned[column] = normalize_string_series(cleaned[column])

    cleaned["show_id"] = cleaned["show_id"].astype("string").str.strip()
    cleaned["date_added"] = parse_date_added(cleaned["date_added"])
    cleaned["date_added_year"] = cleaned["date_added"].dt.year.astype("Int64")
    cleaned["date_added_month"] = cleaned["date_added"].dt.month.astype("Int64")

    cleaned["rating_system"] = cleaned["rating"].apply(infer_rating_system)
    cleaned["rating_group"] = cleaned["rating"].apply(infer_rating_group)
    cleaned["is_unrated"] = cleaned["rating"].isna() | cleaned["rating"].isin(UNRATED_VALUES)

    duration_parts = parse_duration_parts(cleaned["duration"])
    cleaned["duration_value"] = duration_parts["duration_value"]
    cleaned["duration_unit"] = duration_parts["duration_unit"]

    cleaned["release_year"] = cleaned["release_year"].astype("Int64")
    return cleaned


def build_titles_table(cleaned_df: pd.DataFrame) -> pd.DataFrame:
    """Select the analysis-ready base titles table."""
    titles = cleaned_df[TITLES_OUTPUT_COLUMNS].copy()
    titles = titles.sort_values("show_id").reset_index(drop=True)
    return titles


def build_bridge_tables(cleaned_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create normalized bridge tables for multi-value source columns."""
    return {
        "title_country": split_and_explode_column(cleaned_df, "show_id", "country", "country"),
        "title_genre": split_and_explode_column(cleaned_df, "show_id", "listed_in", "genre"),
        "title_cast": split_and_explode_column(cleaned_df, "show_id", "cast", "cast_member"),
        "title_director": split_and_explode_column(cleaned_df, "show_id", "director", "director"),
    }


def build_qa_outputs(
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    titles_df: pd.DataFrame,
    bridge_tables: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Create QA tables that document row preservation and parsing quality."""
    table_counts = [
        {
            "table_name": "raw_titles",
            "row_count": int(len(raw_df)),
            "distinct_show_id": int(raw_df["show_id"].nunique()),
        },
        {
            "table_name": "titles",
            "row_count": int(len(titles_df)),
            "distinct_show_id": int(titles_df["show_id"].nunique()),
        },
    ]
    for table_name, table in bridge_tables.items():
        table_counts.append(
            {
                "table_name": table_name,
                "row_count": int(len(table)),
                "distinct_show_id": int(table["show_id"].nunique()),
            }
        )

    titles_missingness = (
        titles_df.isna()
        .sum()
        .rename("missing_count")
        .reset_index()
        .rename(columns={"index": "column"})
    )
    titles_missingness["missing_share"] = (
        titles_missingness["missing_count"] / len(titles_df)
    ).round(4)
    titles_missingness = titles_missingness.sort_values(
        ["missing_count", "column"], ascending=[False, True]
    ).reset_index(drop=True)

    bridge_coverage_rows = []
    for source_column, value_column in MULTIVALUE_COLUMN_MAP.items():
        table_name = f"title_{'genre' if source_column == 'listed_in' else source_column}"
        bridge = bridge_tables[table_name]
        titles_with_values_raw = int(cleaned_df[source_column].notna().sum())
        titles_with_values_bridge = int(bridge["show_id"].nunique())
        bridge_coverage_rows.append(
            {
                "source_column": source_column,
                "bridge_table": table_name,
                "titles_with_values_raw": titles_with_values_raw,
                "titles_with_values_bridge": titles_with_values_bridge,
                "bridge_rows": int(len(bridge)),
                "avg_values_per_title": round(
                    float(len(bridge) / titles_with_values_bridge), 2
                )
                if titles_with_values_bridge
                else 0.0,
            }
        )

    parse_checks = pd.DataFrame(
        [
            {
                "check_name": "duplicate_show_id_raw",
                "value": int(raw_df["show_id"].duplicated().sum()),
            },
            {
                "check_name": "duplicate_show_id_titles",
                "value": int(titles_df["show_id"].duplicated().sum()),
            },
            {
                "check_name": "raw_date_added_missing",
                "value": int(raw_df["date_added"].isna().sum()),
            },
            {
                "check_name": "date_added_parse_failures_non_missing",
                "value": int(
                    cleaned_df.loc[
                        raw_df["date_added"].notna() & cleaned_df["date_added"].isna()
                    ].shape[0]
                ),
            },
            {
                "check_name": "duration_parse_failures",
                "value": int(cleaned_df["duration_value"].isna().sum()),
            },
            {
                "check_name": "unrated_or_unknown_titles",
                "value": int(titles_df["is_unrated"].sum()),
            },
        ]
    )

    return {
        "qa_table_counts": pd.DataFrame(table_counts),
        "qa_titles_missingness": titles_missingness,
        "qa_bridge_coverage": pd.DataFrame(bridge_coverage_rows),
        "qa_parse_checks": parse_checks,
    }


def build_processed_outputs(raw_df: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    """Run the complete Phase 1 cleaning pipeline and return processed tables."""
    cleaned_df = standardize_titles_frame(raw_df)
    titles_df = build_titles_table(cleaned_df)
    bridge_tables = build_bridge_tables(cleaned_df)
    qa_outputs = build_qa_outputs(raw_df, cleaned_df, titles_df, bridge_tables)
    processed_tables = {"titles": titles_df, **bridge_tables}
    return processed_tables, qa_outputs


def save_processed_outputs(
    processed_tables: dict[str, pd.DataFrame],
    qa_outputs: dict[str, pd.DataFrame],
    output_directory: str | Path,
) -> None:
    """Save processed tables and QA tables into the processed data directory."""
    output_directory = ensure_directory(output_directory)
    for table_name, table in {**processed_tables, **qa_outputs}.items():
        save_dataframe(table, output_directory / f"{table_name}.csv")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the cleaning pipeline."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="data/raw/netflix_titles.csv",
        help="Path to the raw Netflix titles CSV.",
    )
    parser.add_argument(
        "--output",
        default="data/processed",
        help="Directory where processed CSV outputs will be saved.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the cleaning pipeline from the command line."""
    args = parse_args()
    raw_df = read_raw_titles(args.input)
    processed_tables, qa_outputs = build_processed_outputs(raw_df)
    save_processed_outputs(processed_tables, qa_outputs, args.output)
    print(f"Saved {len(processed_tables) + len(qa_outputs)} files to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()

