import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from nir_cp.plots import (
    plot_bland_altman,
    plot_difference_vs_reference,
    plot_old_vs_new,
)


def _example_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sample_id": ["S1", "S2", "S3", "S4"],
            "old_nir": [99.8, 100.2, 100.6, 99.5],
            "new_nir": [99.9, 100.1, 100.7, 99.6],
            "reference": [99.7, 100.3, 100.5, 99.4],
        }
    )


def test_plot_old_vs_new_returns_figure() -> None:
    fig = plot_old_vs_new(_example_df(), sample_id_col="sample_id")

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_bland_altman_returns_figure() -> None:
    fig = plot_bland_altman(_example_df())

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_difference_vs_reference_returns_figure() -> None:
    fig = plot_difference_vs_reference(_example_df())

    assert isinstance(fig, Figure)
    plt.close(fig)
