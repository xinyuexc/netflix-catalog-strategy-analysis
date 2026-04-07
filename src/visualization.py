"""Visualization helpers reserved for later business-facing reporting notebooks."""

from __future__ import annotations

import matplotlib.pyplot as plt


def apply_report_style() -> None:
    """Apply a clean, neutral plotting style for portfolio-ready charts."""
    plt.style.use("tableau-colorblind10")

