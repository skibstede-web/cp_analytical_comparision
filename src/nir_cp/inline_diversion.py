"""Inline NIR diversion-control performance verification helpers."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from nir_cp.process_repeatability import calculate_process_repeatability


PROCESS_REPEATABILITY_NOT_IMPLEMENTED_MESSAGE = (
    "The company-specific process_repeatability algorithm has not yet been provided. "
    "This placeholder remains only for situations where precomputed company-approved "
    "process_repeatability values are used."
)


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _finite_numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    _require_columns(df, [column])
    values = pd.to_numeric(df[column], errors="coerce")
    if values.isna().any() or not np.isfinite(values).all():
        raise ValueError(f"Column must contain finite numeric values: {column}")
    return values


def _positive_finite(value: float, *, name: str) -> float:
    number = float(value)
    if not np.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be a finite value greater than 0.")
    return number


def _finite(value: float, *, name: str) -> float:
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{name} must be finite.")
    return number


def _boolean_series(df: pd.DataFrame, column: str) -> pd.Series:
    _require_columns(df, [column])
    values = df[column]
    if pd.api.types.is_bool_dtype(values):
        return values.astype(bool)

    normalized = values.astype(str).str.strip().str.lower()
    mapping = {
        "true": True,
        "1": True,
        "yes": True,
        "y": True,
        "false": False,
        "0": False,
        "no": False,
        "n": False,
    }
    converted = normalized.map(mapping)
    if converted.isna().any():
        raise ValueError(f"Column must contain boolean-like values: {column}")
    return converted.astype(bool)


def calculate_reference_errors(
    df: pd.DataFrame,
    nir_col: str = "nir_prediction",
    reference_col: str = "reference_result",
) -> pd.DataFrame:
    """Return a copy with NIR-reference error columns."""

    result = df.copy()
    nir_values = _finite_numeric_series(result, nir_col)
    reference_values = _finite_numeric_series(result, reference_col)
    result[nir_col] = nir_values
    result[reference_col] = reference_values
    result["error"] = nir_values - reference_values
    result["absolute_error"] = result["error"].abs()
    result["squared_error"] = result["error"] ** 2
    return result


def summarize_accuracy_vs_reference(
    df: pd.DataFrame,
    nir_col: str = "nir_prediction",
    reference_col: str = "reference_result",
) -> dict[str, float | int]:
    """Summarize inline NIR accuracy against extracted reference samples."""

    errors = calculate_reference_errors(df, nir_col=nir_col, reference_col=reference_col)
    if len(errors) < 2:
        raise ValueError("At least 2 reference samples are required.")

    error = errors["error"]
    return {
        "n": int(len(errors)),
        "mean_bias": float(error.mean()),
        "sd_error": float(error.std(ddof=1)),
        "mae": float(errors["absolute_error"].mean()),
        "rmsep": float(np.sqrt(errors["squared_error"].mean())),
        "min_error": float(error.min()),
        "max_error": float(error.max()),
    }


def classify_diversion_zone(
    df: pd.DataFrame,
    nir_col: str = "nir_prediction",
    lower_col: str = "diversion_lower_limit",
    upper_col: str = "diversion_upper_limit",
    guard_band: float | None = None,
) -> pd.DataFrame:
    """Classify each NIR prediction relative to diversion limits."""

    result = df.copy()
    nir_values = _finite_numeric_series(result, nir_col)
    lower_values = _finite_numeric_series(result, lower_col)
    upper_values = _finite_numeric_series(result, upper_col)
    if (lower_values >= upper_values).any():
        raise ValueError("Each lower diversion limit must be less than the upper limit.")

    result[nir_col] = nir_values
    result[lower_col] = lower_values
    result[upper_col] = upper_values

    zones = pd.Series("within_limits", index=result.index, dtype="object")
    zones = zones.mask(nir_values < lower_values, "below_lower_limit")
    zones = zones.mask(nir_values > upper_values, "above_upper_limit")

    if guard_band is not None:
        guard_band_float = float(guard_band)
        if not np.isfinite(guard_band_float) or guard_band_float < 0:
            raise ValueError("guard_band must be None or a finite non-negative value.")
        if guard_band_float > 0:
            within_limits = (nir_values >= lower_values) & (nir_values <= upper_values)
            lower_guard = within_limits & (nir_values <= lower_values + guard_band_float)
            upper_guard = within_limits & (nir_values >= upper_values - guard_band_float)
            zones = zones.mask(lower_guard, "within_guard_band_lower")
            zones = zones.mask(upper_guard, "within_guard_band_upper")

    result["diversion_zone"] = zones
    return result


def summarize_diversion_decisions(
    df: pd.DataFrame,
    zone_col: str = "diversion_zone",
) -> pd.DataFrame:
    """Summarize diversion zone counts and proportions."""

    _require_columns(df, [zone_col])
    n = len(df)
    if n == 0:
        raise ValueError("At least one diversion decision is required.")

    counts = df[zone_col].value_counts(dropna=False).rename_axis("diversion_zone")
    summary = counts.reset_index(name="count")
    summary["proportion"] = summary["count"] / n
    return summary


def summarize_spectral_diagnostics(
    df: pd.DataFrame,
    valid_col: str = "valid_spectrum",
    q_col: str = "q_residual",
    t2_col: str = "hotelling_t2",
    q_limit: float | None = None,
    t2_limit: float | None = None,
) -> dict[str, float | int | None]:
    """Summarize basic spectral diagnostics and optional exceedance rates."""

    valid_values = _boolean_series(df, valid_col)
    n = int(len(df))
    if n == 0:
        raise ValueError("At least one spectrum is required.")

    result: dict[str, float | int | None] = {
        "n": n,
        "invalid_spectrum_rate": float((~valid_values).mean()),
        "q_residual_exceedance_rate": None,
        "hotelling_t2_exceedance_rate": None,
    }

    if q_limit is not None:
        q_limit_float = _finite(q_limit, name="q_limit")
        q_values = _finite_numeric_series(df, q_col)
        result["q_residual_exceedance_rate"] = float((q_values > q_limit_float).mean())

    if t2_limit is not None:
        t2_limit_float = _finite(t2_limit, name="t2_limit")
        t2_values = _finite_numeric_series(df, t2_col)
        result["hotelling_t2_exceedance_rate"] = float((t2_values > t2_limit_float).mean())

    return result


def compare_new_to_historical_run_summary(
    summary_df: pd.DataFrame,
) -> dict[str, float | int]:
    """Compare one new run to historical old-method process repeatability."""

    _require_columns(summary_df, ["method_status", "run_id", "process_repeatability"])
    working = summary_df.copy()
    working["method_status"] = working["method_status"].astype(str).str.strip().str.lower()
    working["process_repeatability"] = _finite_numeric_series(
        working,
        "process_repeatability",
    )
    if (working["process_repeatability"] <= 0).any():
        raise ValueError("process_repeatability values must be greater than 0.")

    historical = working[working["method_status"] == "old"]
    new = working[working["method_status"] == "new"]
    if len(historical) == 0:
        raise ValueError("At least one historical old run is required.")
    if len(new) != 1:
        raise ValueError("Exactly one new run is required in the run summary.")

    historical_mean = float(historical["process_repeatability"].mean())
    historical_max = float(historical["process_repeatability"].max())
    new_repeatability = float(new["process_repeatability"].iloc[0])

    return {
        "historical_n_runs": int(historical["run_id"].nunique()),
        "new_n_runs": int(new["run_id"].nunique()),
        "historical_mean_process_repeatability": historical_mean,
        "historical_max_process_repeatability": historical_max,
        "new_process_repeatability": new_repeatability,
        "ratio_new_to_historical_mean": float(new_repeatability / historical_mean),
        "ratio_new_to_historical_max": float(new_repeatability / historical_max),
    }


def process_repeatability_placeholder(*args: Any, **kwargs: Any) -> None:
    """Placeholder for the company-specific process repeatability calculation."""

    raise NotImplementedError(PROCESS_REPEATABILITY_NOT_IMPLEMENTED_MESSAGE)


def add_process_repeatability_to_run_summary(
    run_df: pd.DataFrame,
    run_id: str,
    method_status: str,
    batch_id: str | None = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Calculate process_repeatability and return a one-row run summary."""

    result = calculate_process_repeatability(run_df, **kwargs)
    summary = result["summary"]
    return pd.DataFrame(
        [
            {
                "method_status": method_status,
                "run_id": run_id,
                "batch_id": batch_id,
                "n_reference_samples": None,
                "process_repeatability": result["process_repeatability"],
                "process_repeatability_mode": result["mode"],
                "n_residuals": summary["n_residuals"],
                "process_repeatability_unit": result["unit"],
            }
        ]
    )


def inline_verification_decision(
    accuracy_summary: dict[str, Any],
    repeatability_comparison: dict[str, Any],
    d_inline: float,
    k_inline: float,
) -> dict[str, bool | str | float]:
    """Apply preliminary inline diversion-control verification criteria."""

    d_inline_float = _positive_finite(d_inline, name="d_inline")
    k_inline_float = _positive_finite(k_inline, name="k_inline")
    mean_bias = _finite(accuracy_summary["mean_bias"], name="mean_bias")
    ratio_to_mean = _finite(
        repeatability_comparison["ratio_new_to_historical_mean"],
        name="ratio_new_to_historical_mean",
    )

    accuracy_pass = bool(abs(mean_bias) <= d_inline_float)
    repeatability_pass = bool(ratio_to_mean <= k_inline_float)
    overall_pass = bool(accuracy_pass and repeatability_pass)

    if overall_pass:
        decision_text = (
            "Preliminary inline diversion-control verification met the predefined "
            "accuracy and process repeatability criteria. These criteria "
            "must be confirmed or replaced by CP-approved criteria before GMP use."
        )
    else:
        decision_text = (
            "Preliminary inline diversion-control verification did not meet the "
            "predefined accuracy and process repeatability criteria. "
            "These criteria must be confirmed or replaced by CP-approved criteria "
            "before GMP use."
        )

    return {
        "accuracy_pass": accuracy_pass,
        "repeatability_pass": repeatability_pass,
        "overall_pass": overall_pass,
        "decision_text": decision_text,
        "mean_bias": mean_bias,
        "d_inline": d_inline_float,
        "ratio_new_to_historical_mean": ratio_to_mean,
        "k_inline": k_inline_float,
    }
