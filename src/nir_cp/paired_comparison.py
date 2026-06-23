"""Paired old-vs-new NIR method comparison decision helpers."""

from __future__ import annotations

from typing import Any

from nir_cp.statistics_usp1010 import (
    paired_accuracy_equivalence,
    paired_precision_noninferiority_from_duplicate_measurements,
    paired_precision_noninferiority_known_old_variance,
    precision_noninferiority,
)


def paired_comparison_decision(
    old_values: Any,
    new_values: Any,
    d: float,
    k: float,
    alpha_accuracy: float = 0.05,
    alpha_precision: float = 0.05,
    precision_method: str = "observed_sd_ratio_exploratory",
    old_variance: float | None = None,
    old_rep1: Any | None = None,
    old_rep2: Any | None = None,
    new_rep1: Any | None = None,
    new_rep2: Any | None = None,
    allow_exploratory_precision_as_primary: bool = True,
) -> dict[str, object]:
    """Run paired accuracy and selected precision criteria.

    `observed_sd_ratio_exploratory` preserves the original total-observed SD ratio
    behavior for backward compatibility. For heterogeneous paired samples, use
    `known_old_variance` or `duplicate_measurements` as the primary USP <1010>
    paired precision method unless the exploratory method is explicitly justified.
    """

    accuracy = paired_accuracy_equivalence(
        old_values,
        new_values,
        d=d,
        alpha=alpha_accuracy,
    )
    if precision_method == "known_old_variance":
        if old_variance is None:
            raise ValueError("old_variance is required for known_old_variance precision.")
        precision = paired_precision_noninferiority_known_old_variance(
            old_values,
            new_values,
            old_variance=old_variance,
            k=k,
            alpha=alpha_precision,
        )
        precision_is_primary = True
    elif precision_method == "duplicate_measurements":
        if any(value is None for value in (old_rep1, old_rep2, new_rep1, new_rep2)):
            raise ValueError(
                "old_rep1, old_rep2, new_rep1, and new_rep2 are required for "
                "duplicate_measurements precision."
            )
        precision = paired_precision_noninferiority_from_duplicate_measurements(
            old_rep1,
            old_rep2,
            new_rep1,
            new_rep2,
            k=k,
            alpha=alpha_precision,
        )
        precision_is_primary = True
    elif precision_method == "observed_sd_ratio_exploratory":
        precision = precision_noninferiority(
            old_values,
            new_values,
            k=k,
            alpha=alpha_precision,
        )
        precision_is_primary = bool(allow_exploratory_precision_as_primary)
    else:
        raise ValueError(f"Unsupported precision_method: {precision_method}")

    overall_pass = bool(accuracy["pass"] and precision["pass"] and precision_is_primary)

    if overall_pass:
        if precision_method == "observed_sd_ratio_exploratory":
            decision_text = (
                "The changed NIR method met the predefined paired accuracy equivalence "
                "and exploratory observed-SD precision criteria. This precision method "
                "is supportive/exploratory and is not the preferred USP <1010> paired "
                "precision method for heterogeneous samples unless justified."
            )
        else:
            decision_text = (
                "The changed NIR method met the predefined paired accuracy equivalence "
                "and paired precision noninferiority criteria."
            )
    else:
        if precision_method == "observed_sd_ratio_exploratory" and precision["pass"] and not precision_is_primary:
            decision_text = (
                "The changed NIR method did not receive an overall pass because "
                "exploratory observed-SD precision was not allowed as a primary "
                "criterion. Use a CP-approved paired precision method or explicitly "
                "justify exploratory precision use."
            )
        elif precision_method == "observed_sd_ratio_exploratory":
            decision_text = (
                "The changed NIR method did not meet the predefined paired accuracy "
                "equivalence and exploratory observed-SD precision criteria. This "
                "precision method is supportive/exploratory and is not the preferred "
                "USP <1010> paired precision method for heterogeneous samples unless "
                "justified."
            )
        else:
            decision_text = (
                "The changed NIR method did not meet the predefined paired accuracy "
                "equivalence and paired precision noninferiority criteria."
            )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "overall_pass": overall_pass,
        "decision_text": decision_text,
        "precision_method": precision_method,
        "precision_is_primary": precision_is_primary,
    }
