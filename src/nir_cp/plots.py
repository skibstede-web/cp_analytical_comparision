"""Plotting helpers for paired NIR method comparison reports."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")
    values = pd.to_numeric(df[column], errors="coerce")
    if values.isna().any():
        raise ValueError(f"Column must contain numeric values: {column}")
    return values


def plot_old_vs_new(
    df: pd.DataFrame,
    old_col: str = "old_nir",
    new_col: str = "new_nir",
    sample_id_col: str | None = None,
) -> Figure:
    """Create an old-method vs changed-method scatter plot."""

    old_values = _numeric_series(df, old_col)
    new_values = _numeric_series(df, new_col)

    fig, ax = plt.subplots()
    ax.scatter(old_values, new_values)

    axis_min = float(min(old_values.min(), new_values.min()))
    axis_max = float(max(old_values.max(), new_values.max()))
    padding = max((axis_max - axis_min) * 0.05, 0.1)
    limits = [axis_min - padding, axis_max + padding]
    ax.plot(limits, limits, linestyle="--")
    ax.set_xlim(limits)
    ax.set_ylim(limits)
    ax.set_xlabel("Old NIR result")
    ax.set_ylabel("Changed NIR result")
    ax.set_title("Old vs Changed NIR Results")

    if sample_id_col is not None:
        if sample_id_col not in df.columns:
            raise ValueError(f"Column not found: {sample_id_col}")
        for old_value, new_value, sample_id in zip(
            old_values,
            new_values,
            df[sample_id_col],
            strict=True,
        ):
            ax.annotate(str(sample_id), (old_value, new_value), fontsize=8)

    fig.tight_layout()
    return fig


def plot_bland_altman(
    df: pd.DataFrame,
    old_col: str = "old_nir",
    new_col: str = "new_nir",
) -> Figure:
    """Create a Bland-Altman style plot for changed minus old differences."""

    old_values = _numeric_series(df, old_col)
    new_values = _numeric_series(df, new_col)
    averages = (old_values + new_values) / 2
    differences = new_values - old_values
    mean_difference = float(differences.mean())
    sd_difference = float(differences.std(ddof=1))

    fig, ax = plt.subplots()
    ax.scatter(averages, differences)
    ax.axhline(mean_difference, linestyle="-")
    ax.axhline(mean_difference + 1.96 * sd_difference, linestyle="--")
    ax.axhline(mean_difference - 1.96 * sd_difference, linestyle="--")
    ax.set_xlabel("Average of old and changed NIR results")
    ax.set_ylabel("Changed - old NIR result")
    ax.set_title("Bland-Altman Difference Plot")
    fig.tight_layout()
    return fig


def plot_difference_vs_reference(
    df: pd.DataFrame,
    reference_col: str = "reference",
    old_col: str = "old_nir",
    new_col: str = "new_nir",
) -> Figure:
    """Plot changed-minus-old NIR differences against reference values."""

    reference_values = _numeric_series(df, reference_col)
    old_values = _numeric_series(df, old_col)
    new_values = _numeric_series(df, new_col)
    differences = new_values - old_values

    fig, ax = plt.subplots()
    ax.scatter(reference_values, differences)
    ax.axhline(0.0, linestyle="--")
    ax.set_xlabel("Reference result")
    ax.set_ylabel("Changed - old NIR result")
    ax.set_title("Difference vs Reference")
    fig.tight_layout()
    return fig
