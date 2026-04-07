"""Visualization helpers for the Phase 2 business analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

from src.utils import ensure_directory

TYPE_COLORS = {"Movie": "#B85C38", "TV Show": "#3B5B92"}
RATING_COLORS = {
    "Kids": "#4DAF7C",
    "Family": "#A8D977",
    "Teen": "#F5B14C",
    "Mature": "#C44536",
    "Unknown / Unrated": "#9A9A9A",
}
COUNTRY_SCOPE_COLORS = {
    "Missing country": "#B9B9B9",
    "Single-country": "#5F8FC0",
    "Multi-country": "#24476B",
}


def apply_report_style() -> None:
    """Apply a consistent chart style for portfolio-ready business outputs."""
    plt.style.use("default")
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": "#D9D9D9",
            "grid.linewidth": 0.7,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "legend.frameon": False,
            "savefig.bbox": "tight",
            "savefig.dpi": 180,
        }
    )


def save_figure(fig: plt.Figure, output_path: str | Path) -> None:
    """Persist a Matplotlib figure to disk."""
    output_path = Path(output_path)
    ensure_directory(output_path.parent)
    fig.savefig(output_path)


def _format_percent_axis(ax: plt.Axes, xmax: float = 1.0) -> None:
    ax.set_xlim(0, xmax)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))


def _annotate_barh(ax: plt.Axes, values: pd.Series, labels: list[str]) -> None:
    for index, value in enumerate(values):
        ax.text(value + 0.01, index, labels[index], va="center", ha="left", fontsize=9)


def plot_type_mix(type_mix: pd.DataFrame) -> plt.Figure:
    """Plot the title split between Movies and TV Shows."""
    data = type_mix.sort_values("share")
    fig, ax = plt.subplots(figsize=(8, 4.6))
    colors = [TYPE_COLORS.get(value, "#6F6F6F") for value in data["type"]]
    ax.barh(data["type"], data["share"], color=colors)
    _format_percent_axis(ax)
    _annotate_barh(
        ax,
        data["share"],
        [f"{share:.1%} | {count:,} titles" for share, count in zip(data["share"], data["title_count"])],
    )
    ax.set_title("Catalog Mix: Movies Still Dominate the Library")
    ax.set_xlabel("Share of titles")
    ax.set_ylabel("")
    return fig


def plot_stacked_mix(
    mix_df: pd.DataFrame,
    group_column: str,
    category_column: str,
    title: str,
    color_map: dict[str, str],
    group_order: list[str] | None = None,
    category_order: list[str] | None = None,
) -> plt.Figure:
    """Plot a 100% stacked bar chart for grouped categorical mix."""
    pivot = mix_df.pivot(index=group_column, columns=category_column, values="share_within_group").fillna(0.0)
    if group_order is not None:
        pivot = pivot.reindex(group_order)
    if category_order is not None:
        pivot = pivot.reindex(columns=category_order)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    left = np.zeros(len(pivot))
    for category in pivot.columns:
        values = pivot[category].values
        ax.barh(
            pivot.index,
            values,
            left=left,
            color=color_map.get(category, "#6F6F6F"),
            label=category,
        )
        left = left + values

    _format_percent_axis(ax)
    ax.set_title(title)
    ax.set_xlabel("Share within group")
    ax.set_ylabel("")
    ax.legend(loc="lower right", ncol=2)
    return fig


def plot_top_genres_by_type(genre_mix_by_type: pd.DataFrame, top_n: int = 10) -> plt.Figure:
    """Plot the top genres within Movies and TV Shows as side-by-side ranked bars."""
    filtered = genre_mix_by_type[genre_mix_by_type["rank_within_group"] <= top_n].copy()
    groups = filtered["type"].drop_duplicates().tolist()

    fig, axes = plt.subplots(1, len(groups), figsize=(14, 6), sharex=True)
    if len(groups) == 1:
        axes = [axes]

    for ax, group in zip(axes, groups):
        subset = filtered[filtered["type"] == group].sort_values("share_within_group")
        ax.barh(
            subset["genre"],
            subset["share_within_group"],
            color=TYPE_COLORS.get(group, "#6F6F6F"),
        )
        _format_percent_axis(ax, xmax=max(0.24, subset["share_within_group"].max() * 1.15))
        ax.set_title(group)
        ax.set_xlabel("Share within type")
        ax.set_ylabel("")
        ax.tick_params(axis="y", labelsize=9)

    fig.suptitle("Genre Mix by Type Highlights Distinct Catalog Roles", y=1.02, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_concentration_curves(
    genre_curve: pd.DataFrame,
    country_curve: pd.DataFrame,
) -> plt.Figure:
    """Plot cumulative share curves for genres and countries."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    curve_specs = [
        (axes[0], genre_curve, "genre", "Genre concentration"),
        (axes[1], country_curve, "country", "Country concentration"),
    ]

    for ax, frame, column, title in curve_specs:
        ax.plot(frame["entity_rank"], frame["cumulative_share"], color="#1F4E79", linewidth=2.5)
        ax.axhline(0.5, color="#999999", linestyle="--", linewidth=1)
        ax.axhline(0.8, color="#CCCCCC", linestyle="--", linewidth=1)
        ax.set_title(title)
        ax.set_xlabel(f"Top {column}s included")
        ax.set_ylabel("Cumulative share")
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))

    fig.suptitle("Concentration Curves Show a Narrow Country Core and a Moderate Genre Long Tail", y=1.03, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_year_distributions(
    release_year_distribution: pd.DataFrame,
    year_added_distribution: pd.DataFrame,
) -> plt.Figure:
    """Plot release-year and year-added distributions side by side."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))

    axes[0].bar(
        release_year_distribution["release_year"].astype(int),
        release_year_distribution["title_count"],
        color="#507B9C",
    )
    axes[0].set_title("Original release year distribution")
    axes[0].set_xlabel("Release year")
    axes[0].set_ylabel("Titles")

    axes[1].bar(
        year_added_distribution["date_added_year"].astype(int),
        year_added_distribution["title_count"],
        color="#C27C2C",
    )
    axes[1].set_title("Titles added to Netflix by year")
    axes[1].set_xlabel("Year added")
    axes[1].set_ylabel("Titles")

    fig.suptitle("Catalog Growth Came from Recent Releases and a Late Acceleration in Adds", y=1.02, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_release_lag_by_type(title_features: pd.DataFrame) -> plt.Figure:
    """Plot release-to-add lag by content type using boxplots and an overall histogram."""
    data = title_features[title_features["release_to_add_lag_clean"].notna()].copy()
    groups = ["Movie", "TV Show"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    lag_values = [
        data.loc[data["type"] == group, "release_to_add_lag_clean"].astype(float).values
        for group in groups
    ]
    box = axes[0].boxplot(lag_values, labels=groups, patch_artist=True, showfliers=False)
    for patch, group in zip(box["boxes"], groups):
        patch.set_facecolor(TYPE_COLORS.get(group, "#6F6F6F"))
        patch.set_alpha(0.75)
    axes[0].set_title("Release-to-add lag by type")
    axes[0].set_ylabel("Years between release and add")

    clipped = data["release_to_add_lag_clean"].clip(upper=20)
    axes[1].hist(clipped, bins=21, color="#4F6D7A", edgecolor="white")
    axes[1].set_title("Overall lag distribution (clipped at 20 years)")
    axes[1].set_xlabel("Release-to-add lag (years)")
    axes[1].set_ylabel("Titles")

    fig.suptitle("Most Titles Were Added Quickly, but Movies Carry a Longer Legacy Tail", y=1.02, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_freshness_panels(
    freshness_by_type: pd.DataFrame,
    freshness_by_rating: pd.DataFrame,
    freshness_by_genre: pd.DataFrame,
    freshness_by_country: pd.DataFrame,
) -> plt.Figure:
    """Plot share of titles added within three years across key dimensions."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    panels = [
        (axes[0, 0], freshness_by_type.sort_values("share_recent_3y"), "type", "Freshness by type"),
        (
            axes[0, 1],
            freshness_by_rating.sort_values("share_recent_3y"),
            "rating_group",
            "Freshness by rating group",
        ),
        (
            axes[1, 0],
            freshness_by_genre.head(10).sort_values("share_recent_3y"),
            "genre",
            "Freshness by top genres",
        ),
        (
            axes[1, 1],
            freshness_by_country.head(10).sort_values("share_recent_3y"),
            "country",
            "Freshness by top countries",
        ),
    ]

    for ax, frame, label_column, title in panels:
        ax.barh(frame[label_column], frame["share_recent_3y"], color="#4D9078")
        _format_percent_axis(ax)
        ax.set_title(title)
        ax.set_xlabel("Share added within 3 years of release")
        ax.set_ylabel("")
        ax.tick_params(axis="y", labelsize=9)

    fig.suptitle("Freshness Is Strongest in TV-Led and Internationally Expanding Segments", y=1.01, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_country_footprint(
    country_ranking: pd.DataFrame,
    country_scope_by_type: pd.DataFrame,
) -> plt.Figure:
    """Plot the country ranking and single- versus multi-country mix."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    top_countries = country_ranking.head(12).sort_values("share")
    axes[0].barh(top_countries["country"], top_countries["share"], color="#46627F")
    _format_percent_axis(axes[0], xmax=max(0.16, top_countries["share"].max() * 1.15))
    axes[0].set_title("Top production countries in the catalog")
    axes[0].set_xlabel("Share of country-tagged titles")
    axes[0].set_ylabel("")

    pivot = country_scope_by_type.pivot(
        index="type", columns="country_scope", values="share_within_group"
    ).fillna(0.0)
    left = np.zeros(len(pivot))
    for scope in pivot.columns:
        axes[1].barh(
            pivot.index,
            pivot[scope].values,
            left=left,
            color=COUNTRY_SCOPE_COLORS.get(scope, "#6F6F6F"),
            label=scope,
        )
        left = left + pivot[scope].values
    _format_percent_axis(axes[1])
    axes[1].set_title("Single-country versus multi-country mix")
    axes[1].set_xlabel("Share within type")
    axes[1].set_ylabel("")
    axes[1].legend(loc="lower right")

    fig.suptitle("The Geographic Footprint Is International but Built on a Dominant Core", y=1.02, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_country_mix_over_time(country_mix_over_time: pd.DataFrame) -> plt.Figure:
    """Plot how the top countries evolve across year_added."""
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    for country, subset in country_mix_over_time.groupby("country"):
        ordered = subset.sort_values("date_added_year")
        ax.plot(
            ordered["date_added_year"].astype(int),
            ordered["title_count"],
            marker="o",
            linewidth=2.2,
            label=country,
        )
    ax.set_title("Country mix over time for the leading production geographies")
    ax.set_xlabel("Year added")
    ax.set_ylabel("Titles")
    ax.legend(ncol=2)
    return fig


def _plot_heatmap(
    ax: plt.Axes,
    matrix: pd.DataFrame,
    title: str,
    cmap: str,
    center: float | None = None,
    value_format: str = ".0%",
) -> None:
    values = matrix.values.astype(float)
    if center is None:
        image = ax.imshow(values, cmap=cmap, aspect="auto")
    else:
        max_distance = np.nanmax(np.abs(values - center))
        image = ax.imshow(
            values,
            cmap=cmap,
            aspect="auto",
            vmin=center - max_distance,
            vmax=center + max_distance,
        )

    ax.set_xticks(range(matrix.shape[1]))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(range(matrix.shape[0]))
    ax.set_yticklabels(matrix.index)
    ax.set_title(title)

    formatter = (
        (lambda value: f"{value:{value_format}}")
        if not value_format.endswith("%")
        else (lambda value: format(value, value_format))
    )
    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            value = values[row_index, column_index]
            if np.isnan(value):
                label = ""
            elif value_format == ".2f":
                label = f"{value:.2f}"
            else:
                label = formatter(value)
            ax.text(column_index, row_index, label, ha="center", va="center", fontsize=8, color="#111111")

    plt.colorbar(image, ax=ax, fraction=0.046, pad=0.04)


def plot_rating_heatmaps(
    rating_by_genre_matrix: pd.DataFrame,
    rating_by_country_matrix: pd.DataFrame,
) -> plt.Figure:
    """Plot rating mix heatmaps for top genres and top countries."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.4))
    _plot_heatmap(
        axes[0],
        rating_by_genre_matrix,
        "Rating mix across top genres",
        cmap="YlOrRd",
    )
    _plot_heatmap(
        axes[1],
        rating_by_country_matrix,
        "Rating mix across top countries",
        cmap="YlOrRd",
    )
    fig.suptitle("Audience Positioning Shifts Meaningfully Across Genres and Countries", y=1.02, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_pair_lift_heatmap(pair_lift_matrix: pd.DataFrame) -> plt.Figure:
    """Plot a genre-pair lift heatmap for the top genre set."""
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    _plot_heatmap(
        ax,
        pair_lift_matrix,
        "Genre co-occurrence lift among leading catalog buckets",
        cmap="coolwarm",
        center=1.0,
        value_format=".2f",
    )
    fig.tight_layout()
    return fig


def plot_titles_added_profile(
    titles_added_by_year: pd.DataFrame,
    titles_added_by_month: pd.DataFrame,
) -> plt.Figure:
    """Plot annual catalog adds and month-of-year seasonality."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))

    yearly = titles_added_by_year.dropna(subset=["date_added_year"]).copy()
    yearly["date_added_year"] = yearly["date_added_year"].astype(int)
    year_colors = ["#C97B63" if year == yearly["date_added_year"].max() else "#537895" for year in yearly["date_added_year"]]
    axes[0].bar(yearly["date_added_year"].astype(str), yearly["title_count"], color=year_colors)
    axes[0].set_title("Titles added by year")
    axes[0].set_xlabel("Year added")
    axes[0].set_ylabel("Titles")
    axes[0].tick_params(axis="x", rotation=45)

    axes[1].bar(titles_added_by_month["month_name"], titles_added_by_month["share"], color="#A65D57")
    axes[1].set_title("Seasonality of adds by calendar month")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Share of all title adds")
    axes[1].yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))

    fig.suptitle("Catalog Adds Accelerated Sharply and Show a Clear Year-End Bias", y=1.02, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_time_mix_lines(
    mix_df: pd.DataFrame,
    category_column: str,
    value_column: str,
    title: str,
    year_column: str = "date_added_year",
    color_map: dict[str, str] | None = None,
) -> plt.Figure:
    """Plot category shares over time as line charts."""
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    for category, subset in mix_df.groupby(category_column):
        ordered = subset.sort_values(year_column)
        ax.plot(
            ordered[year_column].astype(int),
            ordered[value_column],
            marker="o",
            linewidth=2.2,
            color=None if color_map is None else color_map.get(category),
            label=category,
        )

    ax.set_title(title)
    ax.set_xlabel("Year added")
    ax.set_ylabel("Share within year")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.legend(ncol=2)
    return fig


def plot_time_mix_heatmap(
    matrix: pd.DataFrame,
    title: str,
    cmap: str = "YlOrRd",
) -> plt.Figure:
    """Plot a time-by-category heatmap for mix shifts."""
    fig, ax = plt.subplots(figsize=(10.6, max(4.8, matrix.shape[0] * 0.45)))
    _plot_heatmap(
        ax,
        matrix,
        title=title,
        cmap=cmap,
    )
    fig.tight_layout()
    return fig


def plot_geographic_diversification_over_time(diversification_df: pd.DataFrame) -> plt.Figure:
    """Plot how geographic breadth and concentration change over time."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    ordered = diversification_df.sort_values("date_added_year").copy()
    years = ordered["date_added_year"].astype(int)

    axes[0].plot(years, ordered["distinct_countries"], marker="o", linewidth=2.3, color="#3C6E71")
    axes[0].set_title("Distinct countries represented")
    axes[0].set_xlabel("Year added")
    axes[0].set_ylabel("Countries")

    axes[1].plot(years, ordered["avg_countries_per_title"], marker="o", linewidth=2.3, color="#6A994E")
    axes[1].set_title("Average countries per title")
    axes[1].set_xlabel("Year added")
    axes[1].set_ylabel("Country tags per title")

    axes[2].plot(years, ordered["top_3_country_share"], marker="o", linewidth=2.3, color="#BC6C25", label="Top-3 share")
    axes[2].plot(years, ordered["country_hhi"], marker="o", linewidth=2.3, color="#8C4A3B", label="HHI")
    axes[2].set_title("Geographic concentration")
    axes[2].set_xlabel("Year added")
    axes[2].set_ylabel("Concentration")
    axes[2].yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    axes[2].legend()

    fig.suptitle("Geographic Diversification Expanded Fast Before Concentration Stabilized", y=1.03, fontsize=15, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_cluster_profile_heatmap(profile_matrix: pd.DataFrame) -> plt.Figure:
    """Plot standardized cluster profiles across interpretable business metrics."""
    fig, ax = plt.subplots(figsize=(11.2, max(5.2, profile_matrix.shape[0] * 0.65)))
    _plot_heatmap(
        ax,
        profile_matrix,
        title="Cluster profile heatmap (standardized versus cluster average)",
        cmap="RdYlBu_r",
        center=0.0,
        value_format=".2f",
    )
    fig.tight_layout()
    return fig


def plot_cluster_sizes(
    cluster_summary: pd.DataFrame,
    label_column: str = "cluster_label",
) -> plt.Figure:
    """Plot the relative size of each title cluster."""
    data = cluster_summary.sort_values("cluster_share").copy()
    fig, ax = plt.subplots(figsize=(9.6, 5.4))
    ax.barh(data[label_column], data["cluster_share"], color="#46627F")
    _format_percent_axis(ax)
    _annotate_barh(
        ax,
        data["cluster_share"],
        [f"{share:.1%} | {count:,} titles" for share, count in zip(data["cluster_share"], data["title_count"])],
    )
    ax.set_title("Cluster sizes show a few strategic cores and smaller specialist pockets")
    ax.set_xlabel("Share of titles")
    ax.set_ylabel("")
    return fig


def plot_cast_ecosystem_network(
    cast_nodes: pd.DataFrame,
    cast_edges: pd.DataFrame,
    label_top_n: int = 12,
) -> plt.Figure:
    """Plot the cast co-appearance network for recurring talent ecosystems."""
    import networkx as nx

    graph = nx.Graph()
    for row in cast_edges.itertuples(index=False):
        graph.add_edge(row.source, row.target, weight=row.weight)

    positions = nx.spring_layout(graph, seed=42, weight="weight", k=0.72)
    fig, ax = plt.subplots(figsize=(12.5, 9.5))

    community_ids = sorted(cast_nodes["community_id"].dropna().unique())
    community_palette = plt.cm.get_cmap("tab20", max(len(community_ids), 1))
    size_min = cast_nodes["weighted_degree"].min()
    size_range = max(cast_nodes["weighted_degree"].max() - size_min, 1.0)

    edge_weights = cast_edges["weight"]
    edge_span = max(edge_weights.max() - edge_weights.min(), 1)
    edge_widths = 1.0 + ((edge_weights - edge_weights.min()) / edge_span) * 3.2
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        width=edge_widths.tolist(),
        edge_color="#A7A7A7",
        alpha=0.35,
    )

    for index, community_id in enumerate(community_ids):
        subset = cast_nodes[cast_nodes["community_id"] == community_id].copy()
        node_sizes = 280 + ((subset["weighted_degree"] - size_min) / size_range) * 1200
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=subset["cast_member"].tolist(),
            node_color=[community_palette(index)],
            node_size=node_sizes.tolist(),
            linewidths=0.8,
            edgecolors="white",
            alpha=0.92,
            ax=ax,
        )

    labels = {
        row.cast_member: row.cast_member
        for row in cast_nodes.nlargest(label_top_n, "weighted_degree").itertuples(index=False)
    }
    nx.draw_networkx_labels(graph, positions, labels=labels, font_size=8, font_weight="bold", ax=ax)

    ax.set_title("Recurring Cast Ecosystems Reveal Distinct Talent Communities in the Catalog")
    ax.axis("off")
    return fig
