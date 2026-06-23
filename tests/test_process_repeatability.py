import numpy as np
import pandas as pd
import pytest

from nir_cp.process_repeatability import (
    _validate_time_series_input,
    calculate_process_repeatability,
    local_linear_detrended_residuals,
    process_repeatability_summary_frame,
)


def _trend_df(n: int = 61) -> pd.DataFrame:
    t = np.arange(n, dtype=float)
    noise = 0.08 * np.sin(t / 2.5)
    return pd.DataFrame(
        {
            "timestamp": pd.Timestamp("2026-05-01") + pd.to_timedelta(t, unit="s"),
            "elapsed": t,
            "nir_prediction": 100.0 + 0.01 * t + noise,
            "valid_spectrum": True,
            "q_residual": 0.5,
            "hotelling_t2": 5.0,
        }
    )


def test_local_linear_detrending_removes_linear_trend() -> None:
    result = calculate_process_repeatability(
        _trend_df(),
        window_points=15,
        min_points=9,
    )

    assert result["process_repeatability"] > 0
    assert abs(result["summary"]["mean_residual"]) < 0.01
    assert result["mode"] == "local_linear_detrending"


def test_trending_raw_sd_is_larger_than_detrended_process_repeatability() -> None:
    df = _trend_df()
    df["nir_prediction"] = 100.0 + 0.05 * df["elapsed"] + 0.04 * np.sin(
        df["elapsed"] / 2
    )

    result = calculate_process_repeatability(df, window_points=15, min_points=9)
    raw_sd = df["nir_prediction"].std(ddof=1)

    assert result["process_repeatability"] < raw_sd


def test_valid_spectrum_exclusion_reduces_centre_residuals() -> None:
    df = _trend_df()
    df.loc[[10, 11, 12, 30], "valid_spectrum"] = False

    included = local_linear_detrended_residuals(
        df,
        window_points=15,
        min_points=9,
        exclude_invalid=False,
    )
    excluded = local_linear_detrended_residuals(
        df,
        window_points=15,
        min_points=9,
        exclude_invalid=True,
    )

    assert len(excluded) < len(included)
    assert excluded.attrs["exclusions"]["excluded_invalid"] == 4


def test_invalid_inputs_raise_value_error() -> None:
    df = _trend_df()

    with pytest.raises(ValueError, match="Missing required columns"):
        _validate_time_series_input(df.drop(columns=["timestamp"]), "timestamp", "nir_prediction")
    with pytest.raises(ValueError, match="Missing required columns"):
        _validate_time_series_input(df.drop(columns=["nir_prediction"]), "timestamp", "nir_prediction")
    with pytest.raises(ValueError, match="At least 3 rows"):
        _validate_time_series_input(df.head(2), "timestamp", "nir_prediction")

    duplicated = df.copy()
    duplicated.loc[1, "timestamp"] = duplicated.loc[0, "timestamp"]
    with pytest.raises(ValueError, match="Duplicate timestamps"):
        _validate_time_series_input(duplicated, "timestamp", "nir_prediction")


def test_window_points_mode() -> None:
    result = calculate_process_repeatability(
        _trend_df(),
        time_col="elapsed",
        window_points=13,
        min_points=7,
    )
    frame = process_repeatability_summary_frame(result)

    assert result["parameters"]["window_points"] == 13
    assert result["parameters"]["window_seconds"] is None
    assert frame.loc[0, "mode"] == "local_linear_detrending"


def test_window_seconds_mode() -> None:
    result = calculate_process_repeatability(
        _trend_df(),
        window_seconds=12,
        min_points=7,
    )

    assert result["parameters"]["window_seconds"] == 12
    assert result["summary"]["n_residuals"] > 2
