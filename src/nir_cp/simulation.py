"""Simulation helpers for paired old-vs-new NIR method comparisons."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import pandas as pd

from nir_cp.paired_comparison import paired_comparison_decision


def _validate_count(value: int, *, name: str, minimum: int) -> int:
    count = int(value)
    if count != value or count < minimum:
        raise ValueError(f"{name} must be an integer greater than or equal to {minimum}.")
    return count


def _validate_positive(value: float, *, name: str) -> float:
    number = float(value)
    if not np.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be a finite value greater than 0.")
    return number


def _validate_finite(value: float, *, name: str) -> float:
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{name} must be finite.")
    return number


def _rng(seed: Any) -> np.random.Generator:
    return np.random.default_rng(seed)


def simulate_paired_old_new_data(
    n: int,
    true_bias: float,
    old_sd: float,
    new_sd: float,
    mean: float = 100.0,
    seed: Any = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate paired old-method and changed-method NIR results."""

    n_int = _validate_count(n, name="n", minimum=2)
    true_bias_float = _validate_finite(true_bias, name="true_bias")
    old_sd_float = _validate_positive(old_sd, name="old_sd")
    new_sd_float = _validate_positive(new_sd, name="new_sd")
    mean_float = _validate_finite(mean, name="mean")

    generator = _rng(seed)
    old_values = generator.normal(loc=mean_float, scale=old_sd_float, size=n_int)
    new_values = generator.normal(
        loc=mean_float + true_bias_float,
        scale=new_sd_float,
        size=n_int,
    )
    return old_values, new_values


def simulate_paired_study_dataframe(
    n_samples: int,
    old_mean: float,
    old_sd: float,
    new_mean: float,
    new_sd: float,
    sample_to_sample_sd: float = 0.8,
    reference_sd: float = 0.25,
    seed: Any = None,
    sample_prefix: str = "SYN",
) -> pd.DataFrame:
    """Simulate paired off-line old/new NIR data with shared sample values."""

    n_int = _validate_count(n_samples, name="n_samples", minimum=2)
    old_mean_float = _validate_finite(old_mean, name="old_mean")
    old_sd_float = _validate_positive(old_sd, name="old_sd")
    new_mean_float = _validate_finite(new_mean, name="new_mean")
    new_sd_float = _validate_positive(new_sd, name="new_sd")
    sample_to_sample_sd_float = _validate_positive(
        sample_to_sample_sd,
        name="sample_to_sample_sd",
    )
    reference_sd_float = _validate_positive(reference_sd, name="reference_sd")

    generator = _rng(seed)
    true_values = generator.normal(
        loc=old_mean_float,
        scale=sample_to_sample_sd_float,
        size=n_int,
    )
    true_bias = new_mean_float - old_mean_float
    old_nir = true_values + generator.normal(0, old_sd_float, size=n_int)
    new_nir = true_values + true_bias + generator.normal(0, new_sd_float, size=n_int)
    reference = true_values + generator.normal(0, reference_sd_float, size=n_int)

    return pd.DataFrame(
        {
            "sample_id": [f"{sample_prefix}-{i:03d}" for i in range(1, n_int + 1)],
            "old_nir": old_nir,
            "new_nir": new_nir,
            "reference": reference,
        }
    )


def simulate_granule_assay_study_dataframe(
    n_samples: int,
    old_mean: float,
    old_sd: float,
    new_mean: float,
    new_sd: float,
    sample_to_sample_sd: float = 0.8,
    reference_sd: float = 0.25,
    seed: Any = None,
) -> pd.DataFrame:
    """Simulate granule assay paired study data with report metadata."""

    df = simulate_paired_study_dataframe(
        n_samples=n_samples,
        old_mean=old_mean,
        old_sd=old_sd,
        new_mean=new_mean,
        new_sd=new_sd,
        sample_to_sample_sd=sample_to_sample_sd,
        reference_sd=reference_sd,
        seed=seed,
        sample_prefix="G-SYN",
    )
    n_int = len(df)
    dates = pd.date_range("2026-03-01", periods=n_int, freq="D")
    df.insert(1, "batch_id", [f"G-B{1 + (i // 8):03d}" for i in range(n_int)])
    df.insert(2, "granule_lot", [f"G-L{1 + (i // 6):03d}" for i in range(n_int)])
    df.insert(3, "vial_id", [f"V-{i:03d}" for i in range(1, n_int + 1)])
    df["refill_replicate"] = [(i % 3) + 1 for i in range(n_int)]
    df["analyst"] = [f"GA{(i % 3) + 1:02d}" for i in range(n_int)]
    df["instrument_old"] = "NIR-OLD-GRANULE"
    df["instrument_new"] = "NIR-NEW-GRANULE"
    df["date"] = dates.strftime("%Y-%m-%d")
    return df[
        [
            "sample_id",
            "batch_id",
            "granule_lot",
            "vial_id",
            "old_nir",
            "new_nir",
            "reference",
            "refill_replicate",
            "analyst",
            "instrument_old",
            "instrument_new",
            "date",
        ]
    ]


def simulate_tablet_transmission_study_dataframe(
    n_samples: int,
    old_mean: float,
    old_sd: float,
    new_mean: float,
    new_sd: float,
    sample_to_sample_sd: float = 0.8,
    reference_sd: float = 0.25,
    seed: Any = None,
) -> pd.DataFrame:
    """Simulate tablet transmission paired study data for a fixed path."""

    df = simulate_paired_study_dataframe(
        n_samples=n_samples,
        old_mean=old_mean,
        old_sd=old_sd,
        new_mean=new_mean,
        new_sd=new_sd,
        sample_to_sample_sd=sample_to_sample_sd,
        reference_sd=reference_sd,
        seed=seed,
        sample_prefix="T-SYN",
    )
    n_int = len(df)
    generator = _rng(seed)
    dates = pd.date_range("2026-03-10", periods=n_int, freq="D")
    df.insert(1, "batch_id", [f"T-B{1 + (i // 8):03d}" for i in range(n_int)])
    df.insert(2, "tablet_id", [f"TAB-{i:03d}" for i in range(1, n_int + 1)])
    df.insert(3, "strength", ["100 mg"] * n_int)
    df["tablet_weight"] = generator.normal(250.0, 1.2, size=n_int)
    df["tablet_thickness"] = generator.normal(4.10, 0.04, size=n_int)
    df["instrument_old"] = "NIR-OLD-TABLET"
    df["instrument_new"] = "NIR-NEW-TABLET"
    df["date"] = dates.strftime("%Y-%m-%d")
    return df[
        [
            "sample_id",
            "batch_id",
            "tablet_id",
            "strength",
            "old_nir",
            "new_nir",
            "reference",
            "tablet_weight",
            "tablet_thickness",
            "instrument_old",
            "instrument_new",
            "date",
        ]
    ]


def simulate_paired_comparison_success(
    n: int,
    true_bias: float,
    old_sd: float,
    new_sd: float,
    d: float,
    k: float,
    n_sim: int = 10000,
    seed: Any = 12345,
    alpha_accuracy: float = 0.05,
    alpha_precision: float = 0.05,
) -> dict[str, float | int | Any]:
    """Estimate probability of passing paired old-vs-new NIR comparison criteria."""

    n_int = _validate_count(n, name="n", minimum=2)
    n_sim_int = _validate_count(n_sim, name="n_sim", minimum=1)
    true_bias_float = _validate_finite(true_bias, name="true_bias")
    old_sd_float = _validate_positive(old_sd, name="old_sd")
    new_sd_float = _validate_positive(new_sd, name="new_sd")
    d_float = _validate_positive(d, name="d")
    k_float = _validate_positive(k, name="k")

    generator = _rng(seed)
    pass_accuracy_count = 0
    pass_precision_count = 0
    pass_both_count = 0

    for _ in range(n_sim_int):
        old_values, new_values = simulate_paired_old_new_data(
            n=n_int,
            true_bias=true_bias_float,
            old_sd=old_sd_float,
            new_sd=new_sd_float,
            seed=generator,
        )
        decision = paired_comparison_decision(
            old_values,
            new_values,
            d=d_float,
            k=k_float,
            alpha_accuracy=alpha_accuracy,
            alpha_precision=alpha_precision,
        )
        passed_accuracy = bool(decision["accuracy"]["pass"])
        passed_precision = bool(decision["precision"]["pass"])
        passed_both = bool(decision["overall_pass"])

        pass_accuracy_count += int(passed_accuracy)
        pass_precision_count += int(passed_precision)
        pass_both_count += int(passed_both)

    pass_accuracy_probability = pass_accuracy_count / n_sim_int
    pass_precision_probability = pass_precision_count / n_sim_int
    pass_both_probability = pass_both_count / n_sim_int

    return {
        "n": n_int,
        "true_bias": true_bias_float,
        "old_sd": old_sd_float,
        "new_sd": new_sd_float,
        "d": d_float,
        "k": k_float,
        "n_sim": n_sim_int,
        "seed": seed,
        "alpha_accuracy": alpha_accuracy,
        "alpha_precision": alpha_precision,
        "pass_accuracy_probability": pass_accuracy_probability,
        "pass_precision_probability": pass_precision_probability,
        "pass_both_probability": pass_both_probability,
        "fail_accuracy_probability": 1 - pass_accuracy_probability,
        "fail_precision_probability": 1 - pass_precision_probability,
    }


def sample_size_grid(
    n_values: Iterable[int],
    true_bias_values: Iterable[float],
    sd_ratio_values: Iterable[float],
    old_sd: float,
    d: float,
    k: float,
    n_sim: int = 5000,
    seed: Any = 12345,
) -> pd.DataFrame:
    """Evaluate paired comparison success probability over a scenario grid."""

    old_sd_float = _validate_positive(old_sd, name="old_sd")
    d_float = _validate_positive(d, name="d")
    k_float = _validate_positive(k, name="k")
    n_sim_int = _validate_count(n_sim, name="n_sim", minimum=1)
    n_list = list(n_values)
    true_bias_list = list(true_bias_values)
    sd_ratio_list = list(sd_ratio_values)
    if not n_list:
        raise ValueError("n_values must contain at least one value.")
    if not true_bias_list:
        raise ValueError("true_bias_values must contain at least one value.")
    if not sd_ratio_list:
        raise ValueError("sd_ratio_values must contain at least one value.")

    generator = _rng(seed)
    rows: list[dict[str, float | int]] = []
    for n in n_list:
        n_int = _validate_count(n, name="n", minimum=2)
        for true_bias in true_bias_list:
            true_bias_float = _validate_finite(true_bias, name="true_bias")
            for sd_ratio in sd_ratio_list:
                sd_ratio_float = _validate_positive(sd_ratio, name="sd_ratio")
                new_sd = old_sd_float * sd_ratio_float
                scenario_seed = int(generator.integers(0, np.iinfo(np.int64).max))
                result = simulate_paired_comparison_success(
                    n=n_int,
                    true_bias=true_bias_float,
                    old_sd=old_sd_float,
                    new_sd=new_sd,
                    d=d_float,
                    k=k_float,
                    n_sim=n_sim_int,
                    seed=scenario_seed,
                )
                rows.append(
                    {
                        "n": n_int,
                        "true_bias": true_bias_float,
                        "old_sd": old_sd_float,
                        "new_sd": new_sd,
                        "sd_ratio": sd_ratio_float,
                        "d": d_float,
                        "k": k_float,
                        "pass_accuracy_probability": float(
                            result["pass_accuracy_probability"]
                        ),
                        "pass_precision_probability": float(
                            result["pass_precision_probability"]
                        ),
                        "pass_both_probability": float(result["pass_both_probability"]),
                    }
                )

    return pd.DataFrame.from_records(rows)
