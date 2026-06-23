"""Process repeatability algorithms for inline NIR time series."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _finite_numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    _require_columns(df, [column])
    values = pd.to_numeric(df[column], errors="coerce")
    if values.isna().any() or not np.isfinite(values).all():
        raise ValueError(f"Column must contain finite numeric values: {column}")
    return values.astype(float)


def _boolean_series(values: pd.Series) -> pd.Series:
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
        raise ValueError("valid_col must contain boolean-like values.")
    return converted.astype(bool)


def _validate_time_series_input(
    df: pd.DataFrame,
    time_col: str,
    value_col: str,
) -> pd.DataFrame:
    """Validate and sort a time series, adding `_elapsed_seconds`."""

    _require_columns(df, [time_col, value_col])
    if len(df) < 3:
        raise ValueError("At least 3 rows are required.")

    result = df.copy()
    result["_original_index"] = result.index
    result[value_col] = _finite_numeric_series(result, value_col)

    time_values = result[time_col]
    if pd.api.types.is_numeric_dtype(time_values):
        elapsed = pd.to_numeric(time_values, errors="coerce").astype(float)
        if elapsed.isna().any() or not np.isfinite(elapsed).all():
            raise ValueError(f"Column must contain finite numeric times: {time_col}")
        result["_elapsed_seconds"] = elapsed
    else:
        parsed_time = pd.to_datetime(time_values, errors="coerce")
        if parsed_time.isna().any():
            raise ValueError(f"Column must contain parseable timestamps: {time_col}")
        result[time_col] = parsed_time
        first_time = parsed_time.min()
        result["_elapsed_seconds"] = (
            (parsed_time - first_time).dt.total_seconds().astype(float)
        )

    result = result.sort_values("_elapsed_seconds").reset_index(drop=True)
    if result["_elapsed_seconds"].duplicated().any():
        raise ValueError("Duplicate timestamps are not allowed.")

    return result


def local_linear_detrended_residuals(
    df: pd.DataFrame,
    time_col: str = "timestamp",
    value_col: str = "nir_prediction",
    window_seconds: float | None = None,
    window_points: int = 31,
    min_points: int = 11,
    valid_col: str = "valid_spectrum",
    exclude_invalid: bool = True,
    q_col: str | None = None,
    q_limit: float | None = None,
    t2_col: str | None = None,
    t2_limit: float | None = None,
    exclude_diagnostics: bool = False,
) -> pd.DataFrame:
    """Calculate residuals from local linear detrending around each centre point."""

    if min_points < 2:
        raise ValueError("min_points must be at least 2.")
    if window_seconds is not None and float(window_seconds) <= 0:
        raise ValueError("window_seconds must be greater than 0 when provided.")
    if window_seconds is None and int(window_points) < 2:
        raise ValueError("window_points must be at least 2.")

    working = df.copy()
    n_input_rows = len(working)
    excluded_invalid = 0
    excluded_q = 0
    excluded_t2 = 0

    if exclude_invalid and valid_col in working.columns:
        valid_mask = _boolean_series(working[valid_col])
        excluded_invalid = int((~valid_mask).sum())
        working = working.loc[valid_mask].copy()

    if exclude_diagnostics:
        if q_col is not None and q_limit is not None:
            q_values = _finite_numeric_series(working, q_col)
            q_mask = q_values <= float(q_limit)
            excluded_q = int((~q_mask).sum())
            working = working.loc[q_mask].copy()
        if t2_col is not None and t2_limit is not None:
            t2_values = _finite_numeric_series(working, t2_col)
            t2_mask = t2_values <= float(t2_limit)
            excluded_t2 = int((~t2_mask).sum())
            working = working.loc[t2_mask].copy()

    working = _validate_time_series_input(working, time_col, value_col)
    elapsed = working["_elapsed_seconds"].to_numpy(dtype=float)
    observed = working[value_col].to_numpy(dtype=float)

    rows: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    half_window_seconds = None if window_seconds is None else float(window_seconds) / 2
    window_points_int = int(window_points)
    before = window_points_int // 2
    after = window_points_int - before - 1

    for centre_position, centre_elapsed in enumerate(elapsed):
        if half_window_seconds is not None:
            window_mask = np.abs(elapsed - centre_elapsed) <= half_window_seconds
            window_positions = np.flatnonzero(window_mask)
        else:
            start_position = max(0, centre_position - before)
            end_position = min(len(working), centre_position + after + 1)
            window_positions = np.arange(start_position, end_position)

        if len(window_positions) < min_points:
            skipped.append(
                {
                    "original_index": working.loc[centre_position, "_original_index"],
                    "timestamp": working.loc[centre_position, time_col],
                    "reason": "fewer_than_min_points",
                    "n_points_window": int(len(window_positions)),
                }
            )
            continue

        x = elapsed[window_positions]
        y = observed[window_positions]
        x_centered = x - centre_elapsed
        design = np.column_stack([np.ones(len(x_centered)), x_centered])
        intercept_centered, slope = np.linalg.lstsq(design, y, rcond=None)[0]
        fitted = float(intercept_centered)
        residual = float(observed[centre_position] - fitted)
        local_intercept = float(intercept_centered - slope * centre_elapsed)

        rows.append(
            {
                "original_index": working.loc[centre_position, "_original_index"],
                "timestamp": working.loc[centre_position, time_col],
                "elapsed_seconds": float(centre_elapsed),
                "observed": float(observed[centre_position]),
                "fitted": fitted,
                "residual": residual,
                "local_slope": float(slope),
                "local_intercept": local_intercept,
                "n_points_window": int(len(window_positions)),
                "window_start_time": working.loc[window_positions[0], time_col],
                "window_end_time": working.loc[window_positions[-1], time_col],
            }
        )

    residuals = pd.DataFrame.from_records(rows)
    residuals.attrs["n_input_rows"] = int(n_input_rows)
    residuals.attrs["n_rows_used_for_centres"] = int(len(working))
    residuals.attrs["n_skipped"] = int(len(skipped))
    residuals.attrs["skipped"] = skipped
    residuals.attrs["exclusions"] = {
        "excluded_invalid": excluded_invalid,
        "excluded_q": excluded_q,
        "excluded_t2": excluded_t2,
    }
    residuals.attrs["parameters"] = {
        "time_col": time_col,
        "value_col": value_col,
        "window_seconds": window_seconds,
        "window_points": window_points_int,
        "min_points": int(min_points),
        "valid_col": valid_col,
        "exclude_invalid": bool(exclude_invalid),
        "q_col": q_col,
        "q_limit": q_limit,
        "t2_col": t2_col,
        "t2_limit": t2_limit,
        "exclude_diagnostics": bool(exclude_diagnostics),
    }
    return residuals


def calculate_process_repeatability(
    df: pd.DataFrame,
    time_col: str = "timestamp",
    value_col: str = "nir_prediction",
    window_seconds: float | None = None,
    window_points: int = 31,
    min_points: int = 11,
    valid_col: str = "valid_spectrum",
    exclude_invalid: bool = True,
    q_col: str | None = None,
    q_limit: float | None = None,
    t2_col: str | None = None,
    t2_limit: float | None = None,
    exclude_diagnostics: bool = False,
    unit: str = "assay_units",
) -> dict[str, Any]:
    """Calculate process_repeatability as SD of local linear residuals."""

    residuals = local_linear_detrended_residuals(
        df=df,
        time_col=time_col,
        value_col=value_col,
        window_seconds=window_seconds,
        window_points=window_points,
        min_points=min_points,
        valid_col=valid_col,
        exclude_invalid=exclude_invalid,
        q_col=q_col,
        q_limit=q_limit,
        t2_col=t2_col,
        t2_limit=t2_limit,
        exclude_diagnostics=exclude_diagnostics,
    )
    if len(residuals) < 2:
        raise ValueError("At least 2 residuals are required.")

    residual_values = residuals["residual"]
    residual_median = float(residual_values.median())
    residual_mad = float((residual_values - residual_median).abs().median())
    n_input_rows = int(residuals.attrs["n_input_rows"])
    n_rows_used_for_centres = int(residuals.attrs["n_rows_used_for_centres"])
    n_residuals = int(len(residuals))
    n_skipped = int(residuals.attrs["n_skipped"])
    warnings: list[str] = []
    if n_skipped:
        warnings.append(
            "Some centre points were skipped because their local windows had fewer "
            "than min_points."
        )

    return {
        "process_repeatability": float(residual_values.std(ddof=1)),
        "mode": "local_linear_detrending",
        "unit": unit,
        "parameters": {
            **residuals.attrs["parameters"],
            "unit": unit,
        },
        "summary": {
            "mean_residual": float(residual_values.mean()),
            "residual_median": residual_median,
            "residual_mad": residual_mad,
            "n_input_rows": n_input_rows,
            "n_rows_used_for_centres": n_rows_used_for_centres,
            "n_residuals": n_residuals,
            "n_skipped": n_skipped,
            "percent_rows_used": float(100 * n_residuals / n_input_rows),
            **residuals.attrs["exclusions"],
        },
        "residuals": residuals,
        "warnings": warnings,
    }


def process_repeatability_summary_frame(result: dict[str, Any]) -> pd.DataFrame:
    """Return a one-row reporting summary for process_repeatability."""

    parameters = result["parameters"]
    summary = result["summary"]
    return pd.DataFrame(
        [
            {
                "process_repeatability": result["process_repeatability"],
                "mode": result["mode"],
                "unit": result["unit"],
                "window_seconds": parameters["window_seconds"],
                "window_points": parameters["window_points"],
                "min_points": parameters["min_points"],
                "exclude_invalid": parameters["exclude_invalid"],
                "exclude_diagnostics": parameters["exclude_diagnostics"],
                "n_input_rows": summary["n_input_rows"],
                "n_rows_used_for_centres": summary["n_rows_used_for_centres"],
                "n_residuals": summary["n_residuals"],
                "n_skipped": summary["n_skipped"],
                "percent_rows_used": summary["percent_rows_used"],
                "mean_residual": summary["mean_residual"],
                "residual_median": summary["residual_median"],
                "residual_mad": summary["residual_mad"],
            }
        ]
    )
