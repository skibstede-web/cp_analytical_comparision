"""USP <1010>-aligned statistical helpers for method comparison."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy import stats


def _as_1d_finite_array(values: Any, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be a 1D numeric array-like.")
    if array.size < 2:
        raise ValueError(f"{name} must contain at least 2 observations.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values.")
    return array


def _validate_alpha(alpha: float) -> float:
    alpha_float = float(alpha)
    if not 0 < alpha_float < 0.5:
        raise ValueError("alpha must be greater than 0 and less than 0.5.")
    return alpha_float


def _validate_confidence(confidence: float) -> float:
    confidence_float = float(confidence)
    if not 0 < confidence_float < 1:
        raise ValueError("confidence must be greater than 0 and less than 1.")
    return confidence_float


def _validate_paired_lengths(old_values: np.ndarray, new_values: np.ndarray) -> None:
    if old_values.size != new_values.size:
        raise ValueError("old_values and new_values must have matching paired lengths.")


def mean_ci_t(values: Any, confidence: float = 0.90) -> dict[str, float | int]:
    """Return a two-sided Student t confidence interval for a sample mean."""

    array = _as_1d_finite_array(values, name="values")
    confidence_float = _validate_confidence(confidence)

    n = int(array.size)
    mean = float(np.mean(array))
    sd = float(np.std(array, ddof=1))
    se = float(sd / math.sqrt(n))
    t_quantile = float(stats.t.ppf(1 - (1 - confidence_float) / 2, df=n - 1))
    margin = t_quantile * se

    return {
        "n": n,
        "mean": mean,
        "sd": sd,
        "se": se,
        "confidence": confidence_float,
        "lower": float(mean - margin),
        "upper": float(mean + margin),
    }


def paired_accuracy_equivalence(
    old_values: Any,
    new_values: Any,
    d: float,
    alpha: float = 0.05,
) -> dict[str, float | int | bool]:
    """Evaluate paired mean-difference equivalence using new minus old values."""

    old_array = _as_1d_finite_array(old_values, name="old_values")
    new_array = _as_1d_finite_array(new_values, name="new_values")
    _validate_paired_lengths(old_array, new_array)

    d_float = float(d)
    if d_float <= 0:
        raise ValueError("d must be greater than 0.")
    alpha_float = _validate_alpha(alpha)

    ci_confidence = 1 - 2 * alpha_float
    ci = mean_ci_t(new_array - old_array, confidence=ci_confidence)
    lower = float(ci["lower"])
    upper = float(ci["upper"])

    return {
        "pass": bool(lower >= -d_float and upper <= d_float),
        "d": d_float,
        "alpha": alpha_float,
        "ci_confidence": ci_confidence,
        "mean_difference": float(ci["mean"]),
        "lower": lower,
        "upper": upper,
        "n": int(ci["n"]),
    }


def precision_ratio_upper_bound(
    old_values: Any,
    new_values: Any,
    alpha: float = 0.05,
) -> dict[str, float | int]:
    """Return an independent/observed total SD ratio upper confidence bound.

    This utility uses sample standard deviations from the old and new result arrays
    and an F-distribution bound. It is appropriate for independent homogeneous-
    material precision comparisons or exploratory/supportive total-observed SD
    comparisons. It is not the primary USP <1010> paired precision method for
    heterogeneous paired sample studies unless scientifically justified.
    """

    old_array = _as_1d_finite_array(old_values, name="old_values")
    new_array = _as_1d_finite_array(new_values, name="new_values")
    _validate_paired_lengths(old_array, new_array)
    alpha_float = _validate_alpha(alpha)

    n_old = int(old_array.size)
    n_new = int(new_array.size)
    df_old = n_old - 1
    df_new = n_new - 1
    sd_old = float(np.std(old_array, ddof=1))
    sd_new = float(np.std(new_array, ddof=1))
    if sd_old == 0:
        raise ValueError("old_values sample standard deviation must be greater than 0.")

    variance_ratio = (sd_new**2) / (sd_old**2)
    f_alpha = float(stats.f.ppf(alpha_float, df_new, df_old))
    upper_bound = math.sqrt(variance_ratio / f_alpha)

    return {
        "sd_old": sd_old,
        "sd_new": sd_new,
        "ratio_observed": float(sd_new / sd_old),
        "upper_bound": float(upper_bound),
        "alpha": alpha_float,
        "n_old": n_old,
        "n_new": n_new,
        "df_old": df_old,
        "df_new": df_new,
        "method": "observed_sd_ratio_exploratory",
    }


def precision_noninferiority(
    old_values: Any,
    new_values: Any,
    k: float,
    alpha: float = 0.05,
) -> dict[str, float | int | bool]:
    """Evaluate exploratory observed SD-ratio precision noninferiority.

    This wraps :func:`precision_ratio_upper_bound` and carries the same limitation:
    it is not the primary paired heterogeneous-sample USP <1010> precision method
    unless justified and approved for the study design.
    """

    k_float = float(k)
    if k_float <= 0:
        raise ValueError("k must be greater than 0.")

    result = precision_ratio_upper_bound(old_values, new_values, alpha=alpha)
    return {
        **result,
        "pass": bool(result["upper_bound"] < k_float),
        "k": k_float,
    }


def paired_precision_noninferiority_known_old_variance(
    old_values: Any,
    new_values: Any,
    old_variance: float,
    k: float,
    alpha: float = 0.05,
) -> dict[str, float | int | bool | str]:
    """Evaluate paired precision using paired differences and known old variance."""

    old_array = _as_1d_finite_array(old_values, name="old_values")
    new_array = _as_1d_finite_array(new_values, name="new_values")
    _validate_paired_lengths(old_array, new_array)
    alpha_float = _validate_alpha(alpha)
    old_variance_float = float(old_variance)
    if not np.isfinite(old_variance_float) or old_variance_float <= 0:
        raise ValueError("old_variance must be a finite value greater than 0.")
    k_float = float(k)
    if not np.isfinite(k_float) or k_float <= 0:
        raise ValueError("k must be greater than 0.")

    differences = new_array - old_array
    n = int(differences.size)
    df = n - 1
    paired_difference_variance = float(np.var(differences, ddof=1))
    chi2_alpha_df = float(stats.chi2.ppf(alpha_float, df))
    expression = ((df * paired_difference_variance) / (old_variance_float * chi2_alpha_df)) - 1
    if expression < 0:
        raise ValueError(
            "Known-old-variance paired precision expression under the square root "
            "is negative; review variance inputs and criterion definition."
        )
    upper_bound = math.sqrt(expression)

    return {
        "pass": bool(upper_bound < k_float),
        "k": k_float,
        "alpha": alpha_float,
        "n": n,
        "old_variance": old_variance_float,
        "paired_difference_variance": paired_difference_variance,
        "upper_bound": float(upper_bound),
        "method": "paired_known_old_variance",
    }


def paired_precision_noninferiority_from_duplicate_measurements(
    old_rep1: Any,
    old_rep2: Any,
    new_rep1: Any,
    new_rep2: Any,
    k: float,
    alpha: float = 0.05,
) -> dict[str, float | int | bool | str]:
    """Evaluate paired precision using duplicate old/new measurements."""

    old_rep1_array = _as_1d_finite_array(old_rep1, name="old_rep1")
    old_rep2_array = _as_1d_finite_array(old_rep2, name="old_rep2")
    new_rep1_array = _as_1d_finite_array(new_rep1, name="new_rep1")
    new_rep2_array = _as_1d_finite_array(new_rep2, name="new_rep2")
    sizes = {
        old_rep1_array.size,
        old_rep2_array.size,
        new_rep1_array.size,
        new_rep2_array.size,
    }
    if len(sizes) != 1:
        raise ValueError("Duplicate measurement arrays must have matching lengths.")

    alpha_float = _validate_alpha(alpha)
    k_float = float(k)
    if not np.isfinite(k_float) or k_float <= 0:
        raise ValueError("k must be greater than 0.")

    scale = math.sqrt(2)
    d_old = (old_rep1_array - old_rep2_array) / scale
    d_new = (new_rep1_array - new_rep2_array) / scale
    n = int(d_old.size)
    df_old = n - 1
    df_new = n - 1
    sd_old = float(np.std(d_old, ddof=1))
    sd_new = float(np.std(d_new, ddof=1))
    if sd_old == 0:
        raise ValueError("old duplicate sample standard deviation must be greater than 0.")

    f_alpha = float(stats.f.ppf(alpha_float, df_new, df_old))
    upper_bound = (sd_new / sd_old) * math.sqrt(1 / f_alpha)

    return {
        "pass": bool(upper_bound < k_float),
        "k": k_float,
        "alpha": alpha_float,
        "n": n,
        "sd_old_duplicate": sd_old,
        "sd_new_duplicate": sd_new,
        "observed_ratio": float(sd_new / sd_old),
        "upper_bound": float(upper_bound),
        "method": "paired_duplicate_measurements",
    }
