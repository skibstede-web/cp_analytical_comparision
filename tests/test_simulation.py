import pandas as pd
import pytest

from nir_cp.simulation import (
    sample_size_grid,
    simulate_paired_comparison_success,
    simulate_paired_old_new_data,
)


def test_simulation_success_is_reproducible_with_same_seed() -> None:
    first = simulate_paired_comparison_success(
        n=12,
        true_bias=0.0,
        old_sd=0.4,
        new_sd=0.4,
        d=0.5,
        k=3.0,
        n_sim=100,
        seed=20240623,
    )
    second = simulate_paired_comparison_success(
        n=12,
        true_bias=0.0,
        old_sd=0.4,
        new_sd=0.4,
        d=0.5,
        k=3.0,
        n_sim=100,
        seed=20240623,
    )

    assert first == second


def test_higher_n_does_not_materially_reduce_success_probability() -> None:
    small_n = simulate_paired_comparison_success(
        n=8,
        true_bias=0.0,
        old_sd=0.4,
        new_sd=0.4,
        d=0.5,
        k=3.0,
        n_sim=200,
        seed=123,
    )
    larger_n = simulate_paired_comparison_success(
        n=30,
        true_bias=0.0,
        old_sd=0.4,
        new_sd=0.4,
        d=0.5,
        k=3.0,
        n_sim=200,
        seed=123,
    )

    assert larger_n["pass_both_probability"] >= (
        small_n["pass_both_probability"] - 0.05
    )


def test_large_true_bias_reduces_pass_accuracy_probability() -> None:
    no_bias = simulate_paired_comparison_success(
        n=12,
        true_bias=0.0,
        old_sd=0.2,
        new_sd=0.2,
        d=0.5,
        k=3.0,
        n_sim=150,
        seed=456,
    )
    large_bias = simulate_paired_comparison_success(
        n=12,
        true_bias=1.0,
        old_sd=0.2,
        new_sd=0.2,
        d=0.5,
        k=3.0,
        n_sim=150,
        seed=456,
    )

    assert large_bias["pass_accuracy_probability"] < no_bias[
        "pass_accuracy_probability"
    ]


def test_large_sd_ratio_reduces_pass_precision_probability() -> None:
    similar_sd = simulate_paired_comparison_success(
        n=12,
        true_bias=0.0,
        old_sd=0.3,
        new_sd=0.3,
        d=1.5,
        k=2.0,
        n_sim=150,
        seed=789,
    )
    larger_new_sd = simulate_paired_comparison_success(
        n=12,
        true_bias=0.0,
        old_sd=0.3,
        new_sd=1.5,
        d=1.5,
        k=2.0,
        n_sim=150,
        seed=789,
    )

    assert larger_new_sd["pass_precision_probability"] < similar_sd[
        "pass_precision_probability"
    ]


def test_simulate_paired_old_new_data_validates_inputs() -> None:
    with pytest.raises(ValueError, match="n"):
        simulate_paired_old_new_data(
            n=1,
            true_bias=0.0,
            old_sd=0.3,
            new_sd=0.3,
        )

    with pytest.raises(ValueError, match="old_sd"):
        simulate_paired_old_new_data(
            n=3,
            true_bias=0.0,
            old_sd=0.0,
            new_sd=0.3,
        )

    with pytest.raises(ValueError, match="new_sd"):
        simulate_paired_old_new_data(
            n=3,
            true_bias=0.0,
            old_sd=0.3,
            new_sd=-0.1,
        )


def test_simulate_paired_comparison_success_validates_n_sim() -> None:
    with pytest.raises(ValueError, match="n_sim"):
        simulate_paired_comparison_success(
            n=4,
            true_bias=0.0,
            old_sd=0.3,
            new_sd=0.3,
            d=0.5,
            k=2.0,
            n_sim=0,
        )


def test_sample_size_grid_returns_expected_rows_and_columns() -> None:
    result = sample_size_grid(
        n_values=[6, 8],
        true_bias_values=[0.0, 0.2],
        sd_ratio_values=[1.0, 1.5],
        old_sd=0.3,
        d=0.8,
        k=3.0,
        n_sim=20,
        seed=42,
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 8
    assert list(result.columns) == [
        "n",
        "true_bias",
        "old_sd",
        "new_sd",
        "sd_ratio",
        "d",
        "k",
        "pass_accuracy_probability",
        "pass_precision_probability",
        "pass_both_probability",
    ]
    assert result["pass_both_probability"].between(0, 1).all()


def test_sample_size_grid_validates_sd_ratio() -> None:
    with pytest.raises(ValueError, match="sd_ratio"):
        sample_size_grid(
            n_values=[6],
            true_bias_values=[0.0],
            sd_ratio_values=[0.0],
            old_sd=0.3,
            d=0.8,
            k=3.0,
            n_sim=10,
        )
