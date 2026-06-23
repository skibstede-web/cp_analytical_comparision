import math

import numpy as np
import pytest

from nir_cp.statistics_usp1010 import (
    paired_accuracy_equivalence,
    paired_precision_noninferiority_known_old_variance,
)


def _paired_example_arrays() -> tuple[np.ndarray, np.ndarray]:
    n = 18
    target_mean = 0.39
    target_variance = 0.350
    centered = np.arange(n, dtype=float) - (n - 1) / 2
    scale = math.sqrt(target_variance * (n - 1) / np.sum(centered**2))
    differences = target_mean + scale * centered
    old_values = np.zeros(n)
    new_values = old_values + differences
    return old_values, new_values


def test_paired_accuracy_equivalence_usp1010_numeric_example() -> None:
    old_values, new_values = _paired_example_arrays()

    result = paired_accuracy_equivalence(
        old_values,
        new_values,
        d=1.0,
        alpha=0.05,
    )

    assert result["n"] == 18
    assert result["mean_difference"] == pytest.approx(0.39)
    assert result["lower"] == pytest.approx(0.15, abs=0.02)
    assert result["upper"] == pytest.approx(0.63, abs=0.02)


def test_paired_precision_known_old_variance_usp1010_numeric_example() -> None:
    old_values, new_values = _paired_example_arrays()

    result = paired_precision_noninferiority_known_old_variance(
        old_values,
        new_values,
        old_variance=0.16,
        k=2.0,
        alpha=0.05,
    )

    assert result["method"] == "paired_known_old_variance"
    assert result["n"] == 18
    assert result["paired_difference_variance"] == pytest.approx(0.350)
    assert result["upper_bound"] == pytest.approx(1.81, abs=0.03)
