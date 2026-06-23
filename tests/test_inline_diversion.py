import pandas as pd
import pytest

from nir_cp.inline_diversion import (
    PROCESS_REPEATABILITY_NOT_IMPLEMENTED_MESSAGE,
    add_process_repeatability_to_run_summary,
    calculate_reference_errors,
    classify_diversion_zone,
    compare_new_to_historical_run_summary,
    inline_verification_decision,
    process_repeatability_placeholder,
    summarize_accuracy_vs_reference,
    summarize_diversion_decisions,
    summarize_spectral_diagnostics,
)


def _reference_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "nir_prediction": [99.8, 100.2, 101.1, 98.9],
            "reference_result": [99.7, 100.4, 101.0, 99.0],
            "diversion_lower_limit": [98.0, 98.0, 98.0, 98.0],
            "diversion_upper_limit": [102.0, 102.0, 102.0, 102.0],
            "valid_spectrum": [True, True, False, True],
            "q_residual": [0.5, 1.4, 2.2, 0.8],
            "hotelling_t2": [4.0, 8.5, 6.0, 10.0],
        }
    )


def test_calculate_reference_errors() -> None:
    result = calculate_reference_errors(_reference_df())

    assert result["error"].tolist() == pytest.approx([0.1, -0.2, 0.1, -0.1])
    assert result["absolute_error"].tolist() == pytest.approx([0.1, 0.2, 0.1, 0.1])
    assert result["squared_error"].tolist() == pytest.approx([0.01, 0.04, 0.01, 0.01])


def test_summarize_accuracy_vs_reference_values_are_sensible() -> None:
    result = summarize_accuracy_vs_reference(_reference_df())

    assert result["n"] == 4
    assert result["mean_bias"] == pytest.approx(-0.025)
    assert result["mae"] == pytest.approx(0.125)
    assert result["rmsep"] > 0
    assert result["min_error"] < result["max_error"]


def test_classify_diversion_zone_with_guard_band() -> None:
    df = pd.DataFrame(
        {
            "nir_prediction": [97.5, 98.2, 100.0, 101.8, 102.5],
            "diversion_lower_limit": [98.0] * 5,
            "diversion_upper_limit": [102.0] * 5,
        }
    )

    result = classify_diversion_zone(df, guard_band=0.3)

    assert result["diversion_zone"].tolist() == [
        "below_lower_limit",
        "within_guard_band_lower",
        "within_limits",
        "within_guard_band_upper",
        "above_upper_limit",
    ]
    summary = summarize_diversion_decisions(result)
    assert summary["count"].sum() == 5
    assert summary["proportion"].sum() == pytest.approx(1.0)


def test_summarize_spectral_diagnostics() -> None:
    result = summarize_spectral_diagnostics(
        _reference_df(),
        q_limit=1.5,
        t2_limit=8.0,
    )

    assert result["n"] == 4
    assert result["invalid_spectrum_rate"] == pytest.approx(0.25)
    assert result["q_residual_exceedance_rate"] == pytest.approx(0.25)
    assert result["hotelling_t2_exceedance_rate"] == pytest.approx(0.5)


def test_compare_new_to_historical_run_summary() -> None:
    summary_df = pd.DataFrame(
        {
            "method_status": ["old", "old", "new"],
            "run_id": ["OLD-001", "OLD-002", "NEW-001"],
            "process_repeatability": [0.35, 0.45, 0.40],
        }
    )

    result = compare_new_to_historical_run_summary(summary_df)

    assert result["historical_n_runs"] == 2
    assert result["new_n_runs"] == 1
    assert result["historical_mean_process_repeatability"] == pytest.approx(0.40)
    assert result["historical_max_process_repeatability"] == pytest.approx(0.45)
    assert result["ratio_new_to_historical_mean"] == pytest.approx(1.0)


def test_compare_new_to_historical_requires_exactly_one_new_run() -> None:
    summary_df = pd.DataFrame(
        {
            "method_status": ["old", "new", "new"],
            "run_id": ["OLD-001", "NEW-001", "NEW-002"],
            "process_repeatability": [0.35, 0.40, 0.42],
        }
    )

    with pytest.raises(ValueError, match="Exactly one new run"):
        compare_new_to_historical_run_summary(summary_df)


def test_process_repeatability_placeholder_raises() -> None:
    with pytest.raises(NotImplementedError, match=PROCESS_REPEATABILITY_NOT_IMPLEMENTED_MESSAGE):
        process_repeatability_placeholder()


def test_add_process_repeatability_to_run_summary() -> None:
    t = list(range(31))
    run_df = pd.DataFrame(
        {
            "timestamp": t,
            "nir_prediction": [100 + 0.02 * x + 0.05 * ((-1) ** x) for x in t],
            "valid_spectrum": True,
        }
    )

    result = add_process_repeatability_to_run_summary(
        run_df,
        run_id="NEW-INL-001",
        method_status="new",
        batch_id="SYN-NB001",
        time_col="timestamp",
        window_points=11,
        min_points=7,
    )

    assert len(result) == 1
    assert result.loc[0, "method_status"] == "new"
    assert result.loc[0, "process_repeatability"] > 0
    assert result.loc[0, "process_repeatability_mode"] == "local_linear_detrending"
    assert result.loc[0, "n_residuals"] > 1


def test_inline_verification_decision_passes() -> None:
    result = inline_verification_decision(
        accuracy_summary={"mean_bias": 0.2},
        repeatability_comparison={"ratio_new_to_historical_mean": 1.1},
        d_inline=0.5,
        k_inline=1.5,
    )

    assert result["accuracy_pass"] is True
    assert result["repeatability_pass"] is True
    assert result["overall_pass"] is True
    assert "met the predefined" in result["decision_text"]


def test_inline_verification_decision_fails_with_high_bias_or_repeatability() -> None:
    high_bias = inline_verification_decision(
        accuracy_summary={"mean_bias": 0.8},
        repeatability_comparison={"ratio_new_to_historical_mean": 1.1},
        d_inline=0.5,
        k_inline=1.5,
    )
    high_repeatability = inline_verification_decision(
        accuracy_summary={"mean_bias": 0.2},
        repeatability_comparison={"ratio_new_to_historical_mean": 1.8},
        d_inline=0.5,
        k_inline=1.5,
    )

    assert high_bias["overall_pass"] is False
    assert high_bias["accuracy_pass"] is False
    assert high_repeatability["overall_pass"] is False
    assert high_repeatability["repeatability_pass"] is False
