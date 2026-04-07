"""Metric helpers for Phase 2 business analysis."""

from __future__ import annotations

from itertools import combinations

import networkx as nx
import pandas as pd

from src.utils import MONTH_NAME_MAP


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


def calendar_month_profile(
    df: pd.DataFrame,
    month_column: str = "date_added_month",
    id_column: str = "show_id",
) -> pd.DataFrame:
    """Return a month-of-year profile for titles added to the catalog."""
    working = df[[id_column, month_column]].drop_duplicates().dropna(subset=[month_column]).copy()
    working[month_column] = working[month_column].astype(int)

    summary = (
        working.groupby(month_column)[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
        .sort_values(month_column)
        .reset_index(drop=True)
    )
    summary["month_name"] = summary[month_column].map(MONTH_NAME_MAP)
    summary["share"] = summary["title_count"] / summary["title_count"].sum()
    return summary


def mix_over_time(
    df: pd.DataFrame,
    category_column: str,
    year_column: str = "date_added_year",
    id_column: str = "show_id",
    top_n_categories: int | None = None,
) -> pd.DataFrame:
    """Return annual category counts and shares across the title timeline."""
    working = (
        df[[id_column, year_column, category_column]]
        .drop_duplicates()
        .dropna(subset=[year_column, category_column])
        .copy()
    )
    working[category_column] = working[category_column].astype("string")

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
        working.groupby([year_column, category_column])[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
    )
    summary["year_total"] = summary.groupby(year_column)["title_count"].transform("sum")
    summary["share_within_year"] = summary["title_count"] / summary["year_total"]
    return summary.sort_values([year_column, "title_count"], ascending=[True, False]).reset_index(drop=True)


def geographic_diversification_over_time(
    country_view: pd.DataFrame,
    year_column: str = "date_added_year",
    id_column: str = "show_id",
    country_column: str = "country",
) -> pd.DataFrame:
    """Measure how country breadth and concentration shift over time."""
    working = (
        country_view[[id_column, year_column, country_column]]
        .drop_duplicates()
        .dropna(subset=[year_column, country_column])
        .copy()
    )

    rows = []
    for year, group in working.groupby(year_column):
        country_counts = (
            group.groupby(country_column)[id_column].nunique().sort_values(ascending=False)
        )
        shares = country_counts / country_counts.sum()
        rows.append(
            {
                year_column: year,
                "title_count": int(group[id_column].nunique()),
                "country_tag_count": int(country_counts.sum()),
                "distinct_countries": int(country_counts.index.nunique()),
                "avg_countries_per_title": float(country_counts.sum() / group[id_column].nunique()),
                "country_hhi": float((shares.pow(2)).sum()),
                "top_3_country_share": float(shares.head(3).sum()),
            }
        )

    return pd.DataFrame(rows).sort_values(year_column).reset_index(drop=True)


def _prepare_segmentation_matrix(
    segmentation_df: pd.DataFrame,
    numeric_columns: list[str],
    categorical_columns: list[str],
    binary_columns: list[str],
):
    """Build a feature matrix for interpretable title clustering."""
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    modeling = segmentation_df[numeric_columns + categorical_columns + binary_columns].copy()

    for column in numeric_columns:
        modeling[column] = pd.to_numeric(modeling[column], errors="coerce")
        if modeling[column].isna().any():
            modeling[column] = modeling[column].fillna(modeling[column].median())

    for column in binary_columns:
        modeling[column] = modeling[column].astype(int)

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric_columns),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_columns,
            ),
            ("binary", "passthrough", binary_columns),
        ],
        sparse_threshold=0.0,
    )

    matrix = preprocessor.fit_transform(modeling)
    return modeling, matrix, preprocessor


def evaluate_kmeans_cluster_range(
    segmentation_df: pd.DataFrame,
    numeric_columns: list[str],
    categorical_columns: list[str],
    binary_columns: list[str],
    cluster_values: range | list[int],
    random_state: int = 42,
) -> pd.DataFrame:
    """Compare a small set of KMeans options for interpretability and balance."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    _, matrix, _ = _prepare_segmentation_matrix(
        segmentation_df,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        binary_columns=binary_columns,
    )

    rows = []
    for cluster_count in cluster_values:
        model = KMeans(n_clusters=cluster_count, n_init=25, random_state=random_state)
        labels = model.fit_predict(matrix)
        cluster_shares = pd.Series(labels).value_counts(normalize=True).sort_index()
        rows.append(
            {
                "cluster_count": int(cluster_count),
                "silhouette_score": float(silhouette_score(matrix, labels)),
                "min_cluster_share": float(cluster_shares.min()),
                "max_cluster_share": float(cluster_shares.max()),
                "cluster_share_vector": "|".join(f"{value:.3f}" for value in cluster_shares.tolist()),
            }
        )

    return pd.DataFrame(rows).sort_values("cluster_count").reset_index(drop=True)


def fit_kmeans_segmentation(
    segmentation_df: pd.DataFrame,
    numeric_columns: list[str],
    categorical_columns: list[str],
    binary_columns: list[str],
    cluster_count: int,
    random_state: int = 42,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Fit the chosen interpretable KMeans segmentation and attach cluster ids."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    _, matrix, preprocessor = _prepare_segmentation_matrix(
        segmentation_df,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        binary_columns=binary_columns,
    )
    model = KMeans(n_clusters=cluster_count, n_init=25, random_state=random_state)
    labels = model.fit_predict(matrix)

    clustered = segmentation_df.copy()
    clustered["cluster_id"] = labels.astype(int)

    metadata = {
        "silhouette_score": float(silhouette_score(matrix, labels)),
        "feature_matrix_shape": matrix.shape,
        "feature_names": list(preprocessor.get_feature_names_out()),
    }
    return clustered, metadata


def cluster_summary(
    clustered_titles: pd.DataFrame,
    cluster_column: str = "cluster_id",
    id_column: str = "show_id",
) -> pd.DataFrame:
    """Profile the business shape of each title cluster."""
    working = clustered_titles[[cluster_column, id_column, "type", "rating_group", "release_year", "release_to_add_lag_clean", "country_count", "genre_count", "is_recent_within_3y"]].drop_duplicates().copy()

    summary = (
        working.groupby(cluster_column).agg(
            title_count=(id_column, "nunique"),
            movie_share=("type", lambda values: values.eq("Movie").mean()),
            tv_share=("type", lambda values: values.eq("TV Show").mean()),
            mature_share=("rating_group", lambda values: values.eq("Mature").mean()),
            kids_share=("rating_group", lambda values: values.eq("Kids").mean()),
            median_release_year=("release_year", "median"),
            median_lag=("release_to_add_lag_clean", "median"),
            multi_country_share=("country_count", lambda values: values.gt(1).mean()),
            recent_share=("is_recent_within_3y", "mean"),
            median_country_count=("country_count", "median"),
            median_genre_count=("genre_count", "median"),
        )
    ).reset_index()

    summary["cluster_share"] = summary["title_count"] / summary["title_count"].sum()
    return summary.sort_values(cluster_column).reset_index(drop=True)


def cluster_dimension_profile(
    clustered_bridge: pd.DataFrame,
    dimension_column: str,
    cluster_column: str = "cluster_id",
    id_column: str = "show_id",
    top_n: int | None = 5,
) -> pd.DataFrame:
    """Summarize which dimensions over-index within each cluster."""
    working = (
        clustered_bridge[[cluster_column, id_column, dimension_column]]
        .drop_duplicates()
        .dropna(subset=[dimension_column])
        .copy()
    )
    overall_share = (
        working.groupby(dimension_column)[id_column].nunique() / working[id_column].nunique()
    )

    summary = (
        working.groupby([cluster_column, dimension_column])[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
    )
    cluster_totals = working.groupby(cluster_column)[id_column].nunique()
    summary["cluster_total_titles"] = summary[cluster_column].map(cluster_totals)
    summary["share_within_cluster"] = summary["title_count"] / summary["cluster_total_titles"]
    summary["overall_title_share"] = summary[dimension_column].map(overall_share)
    summary["lift_vs_overall"] = summary["share_within_cluster"] / summary["overall_title_share"]
    summary["rank_within_cluster"] = (
        summary.groupby(cluster_column)["title_count"].rank(method="first", ascending=False).astype(int)
    )

    if top_n is not None:
        summary = summary[summary["rank_within_cluster"] <= top_n].copy()

    return summary.sort_values([cluster_column, "rank_within_cluster"]).reset_index(drop=True)


def standardized_profile_matrix(
    summary_df: pd.DataFrame,
    index_column: str,
    value_columns: list[str],
) -> pd.DataFrame:
    """Standardize selected cluster metrics for a heatmap-friendly profile matrix."""
    matrix = summary_df.set_index(index_column)[value_columns].astype(float)
    return matrix.apply(
        lambda series: (series - series.mean()) / (series.std(ddof=0) or 1.0),
        axis=0,
    )


def repeated_people_summary(
    primary_bridge: pd.DataFrame,
    primary_column: str,
    counterpart_bridge: pd.DataFrame | None = None,
    counterpart_column: str | None = None,
    id_column: str = "show_id",
    top_n: int | None = 20,
) -> pd.DataFrame:
    """Profile repeat presence of people and the breadth of their collaborations."""
    working = (
        primary_bridge[[id_column, primary_column]]
        .drop_duplicates()
        .dropna(subset=[primary_column])
        .copy()
    )
    summary = (
        working.groupby(primary_column)[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
    )

    if counterpart_bridge is not None and counterpart_column is not None:
        counterpart = (
            counterpart_bridge[[id_column, counterpart_column]]
            .drop_duplicates()
            .dropna(subset=[counterpart_column])
        )
        breadth = (
            working.merge(counterpart, on=id_column, how="left")
            .dropna(subset=[counterpart_column])
            .groupby(primary_column)[counterpart_column]
            .nunique()
            .rename(f"unique_{counterpart_column}_partners")
            .reset_index()
        )
        summary = summary.merge(breadth, on=primary_column, how="left")

    summary = summary.fillna(0).sort_values(summary.columns.tolist()[1:], ascending=False)
    if top_n is not None:
        summary = summary.head(top_n).copy()
    return summary.reset_index(drop=True)


def director_cast_collaboration_table(
    title_director: pd.DataFrame,
    title_cast: pd.DataFrame,
    id_column: str = "show_id",
    min_titles: int = 2,
    top_n: int | None = 25,
) -> pd.DataFrame:
    """Return the strongest recurring director-cast pairings."""
    pairs = (
        title_director[[id_column, "director"]]
        .drop_duplicates()
        .merge(title_cast[[id_column, "cast_member"]].drop_duplicates(), on=id_column, how="inner")
    )
    summary = (
        pairs.groupby(["director", "cast_member"])[id_column]
        .nunique()
        .rename("title_count")
        .reset_index()
    )
    summary = summary[summary["title_count"] >= min_titles].copy()
    summary = summary.sort_values("title_count", ascending=False).reset_index(drop=True)
    if top_n is not None:
        summary = summary.head(top_n).copy()
    return summary


def build_cast_coappearance_network(
    title_cast: pd.DataFrame,
    id_column: str = "show_id",
    top_n_cast: int = 60,
    min_edge_weight: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create a cast co-appearance network for the most repeated talent hubs."""
    working = (
        title_cast[[id_column, "cast_member"]]
        .drop_duplicates()
        .dropna(subset=["cast_member"])
        .copy()
    )
    top_cast = (
        working.groupby("cast_member")[id_column]
        .nunique()
        .sort_values(ascending=False)
        .head(top_n_cast)
    )
    filtered = working[working["cast_member"].isin(top_cast.index)].copy()

    edge_weights: dict[tuple[str, str], int] = {}
    for cast_list in filtered.groupby(id_column)["cast_member"].apply(lambda values: sorted(set(values))):
        for source, target in combinations(cast_list, 2):
            edge_weights[(source, target)] = edge_weights.get((source, target), 0) + 1

    edges = pd.DataFrame(
        [
            {"source": source, "target": target, "weight": weight}
            for (source, target), weight in edge_weights.items()
            if weight >= min_edge_weight
        ]
    )

    if edges.empty:
        empty_nodes = pd.DataFrame(columns=["cast_member", "title_count", "weighted_degree", "component_id", "community_id"])
        empty_communities = pd.DataFrame(columns=["community_id", "node_count", "representative_members"])
        return edges, empty_nodes, empty_communities

    graph = nx.Graph()
    for row in edges.itertuples(index=False):
        graph.add_edge(row.source, row.target, weight=row.weight)

    weighted_degree = dict(graph.degree(weight="weight"))
    component_map: dict[str, int] = {}
    for component_id, component_nodes in enumerate(
        sorted(nx.connected_components(graph), key=len, reverse=True),
        start=1,
    ):
        for node in component_nodes:
            component_map[node] = component_id

    communities = sorted(
        nx.algorithms.community.greedy_modularity_communities(graph, weight="weight"),
        key=len,
        reverse=True,
    )
    community_map: dict[str, int] = {}
    for community_id, members in enumerate(communities, start=1):
        for node in members:
            community_map[node] = community_id

    nodes = pd.DataFrame({"cast_member": list(graph.nodes())})
    nodes["title_count"] = nodes["cast_member"].map(top_cast.to_dict()).astype(int)
    nodes["weighted_degree"] = nodes["cast_member"].map(weighted_degree).astype(float)
    nodes["component_id"] = nodes["cast_member"].map(component_map).astype(int)
    nodes["community_id"] = nodes["cast_member"].map(community_map).astype(int)
    nodes = nodes.sort_values(["community_id", "weighted_degree"], ascending=[True, False]).reset_index(drop=True)

    community_rows = []
    for community_id, group in nodes.groupby("community_id"):
        representative_members = ", ".join(group.nlargest(5, "weighted_degree")["cast_member"].tolist())
        community_rows.append(
            {
                "community_id": int(community_id),
                "node_count": int(len(group)),
                "total_weighted_degree": float(group["weighted_degree"].sum()),
                "representative_members": representative_members,
            }
        )

    community_summary = pd.DataFrame(community_rows).sort_values(
        ["node_count", "total_weighted_degree"], ascending=[False, False]
    ).reset_index(drop=True)

    return edges.sort_values("weight", ascending=False).reset_index(drop=True), nodes, community_summary
