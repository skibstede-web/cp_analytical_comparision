"""Regulatory-style text helpers for NIR comparison reports."""

from __future__ import annotations

from typing import Any


def _fmt(value: Any, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def paired_decision_summary_text(
    result: dict[str, Any],
    method_name: str = "Off-line NIR method",
) -> str:
    """Return a concise report paragraph for a paired comparison decision."""

    accuracy = result["accuracy"]
    precision = result["precision"]
    overall_pass = bool(result["overall_pass"])

    if overall_pass:
        decision_sentence = (
            f"{method_name} met the predefined criteria for paired accuracy "
            "equivalence and precision noninferiority."
        )
    else:
        decision_sentence = (
            f"{method_name} did not meet the predefined criteria for paired accuracy "
            "equivalence and precision noninferiority."
        )

    accuracy_sentence = (
        "The paired mean difference "
        f"(new - old) was {_fmt(accuracy['mean_difference'])}, with a "
        f"{_fmt(100 * accuracy['ci_confidence'], digits=1)}% confidence interval "
        f"from {_fmt(accuracy['lower'])} to {_fmt(accuracy['upper'])}; the "
        f"predefined equivalence margin was +/-{_fmt(accuracy['d'])}."
    )
    precision_sentence = (
        "The upper confidence bound for the precision ratio "
        f"(sigma_new / sigma_old) was {_fmt(precision['upper_bound'])}, compared "
        f"with the predefined limit k={_fmt(precision['k'])}."
    )

    return f"{decision_sentence} {accuracy_sentence} {precision_sentence}"


def inline_verification_summary_text(
    result: dict[str, Any],
    method_name: str = "Inline NIR diversion-control method",
) -> str:
    """Return a concise report paragraph for inline diversion verification."""

    if bool(result["overall_pass"]):
        decision_sentence = (
            f"{method_name} met the predefined criteria for preliminary inline "
            "diversion-control verification."
        )
    else:
        decision_sentence = (
            f"{method_name} did not meet the predefined criteria for preliminary "
            "inline diversion-control verification."
        )

    accuracy_sentence = (
        f"The observed mean bias versus reference was {_fmt(result['mean_bias'])}, "
        f"compared with the preliminary limit +/-{_fmt(result['d_inline'])}."
    )
    repeatability_mode = result.get("process_repeatability_mode")
    n_residuals = result.get("n_residuals")
    window_points = result.get("process_repeatability_window_points")
    window_seconds = result.get("process_repeatability_window_seconds")
    if repeatability_mode == "local_linear_detrending":
        if window_seconds is not None:
            window_text = f"window_seconds={_fmt(window_seconds)}"
        else:
            window_text = f"window_points={int(window_points)}"
        repeatability_basis = (
            "new-run process_repeatability was calculated from local linear "
            f"detrending residuals ({window_text}, n_residuals={int(n_residuals)}). "
        )
    else:
        repeatability_basis = "new-run process_repeatability was precomputed. "

    repeatability_sentence = (
        f"{repeatability_basis}The observed ratio to the historical mean was "
        f"{_fmt(result['ratio_new_to_historical_mean'])}, compared with the "
        f"preliminary limit k={_fmt(result['k_inline'])}."
    )
    qualification_sentence = (
        "This statement uses the reported process_repeatability basis and preliminary "
        "criteria that must be confirmed or replaced by CP-approved criteria before "
        "GMP use."
    )

    return (
        f"{decision_sentence} {accuracy_sentence} {repeatability_sentence} "
        f"{qualification_sentence}"
    )
