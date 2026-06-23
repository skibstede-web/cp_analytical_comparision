from nir_cp.paired_comparison import paired_comparison_decision
import pytest


def test_paired_comparison_decision_passes_when_both_criteria_pass() -> None:
    old = [100.0, 101.0, 99.0, 100.5, 98.5, 101.5]
    new = [100.1, 101.1, 98.9, 100.4, 98.6, 101.4]

    result = paired_comparison_decision(old, new, d=0.5, k=3.0)

    assert result["overall_pass"] is True
    assert result["accuracy"]["pass"] is True
    assert result["precision"]["pass"] is True
    assert "met the predefined paired accuracy equivalence" in result["decision_text"]


def test_paired_comparison_decision_fails_when_accuracy_fails() -> None:
    old = [100.0, 101.0, 99.0, 100.5, 98.5, 101.5]
    new = [101.2, 102.2, 100.2, 101.7, 99.7, 102.7]

    result = paired_comparison_decision(old, new, d=0.5, k=3.0)

    assert result["overall_pass"] is False
    assert result["accuracy"]["pass"] is False
    assert "did not meet" in result["decision_text"]


def test_paired_comparison_decision_known_old_variance() -> None:
    old = [100.0, 101.0, 99.0, 100.5, 98.5, 101.5]
    new = [100.1, 101.1, 98.9, 100.4, 98.6, 101.4]

    result = paired_comparison_decision(
        old,
        new,
        d=0.5,
        k=3.0,
        precision_method="known_old_variance",
        old_variance=0.01,
    )

    assert result["overall_pass"] is True
    assert result["precision"]["method"] == "paired_known_old_variance"
    assert result["precision_is_primary"] is True


def test_paired_comparison_decision_requires_old_variance() -> None:
    with pytest.raises(ValueError, match="old_variance"):
        paired_comparison_decision(
            [1.0, 2.0, 3.0],
            [1.1, 2.1, 3.1],
            d=1.0,
            k=2.0,
            precision_method="known_old_variance",
        )


def test_exploratory_precision_not_primary_unless_allowed() -> None:
    result = paired_comparison_decision(
        [100.0, 101.0, 99.0, 100.5, 98.5, 101.5],
        [100.1, 101.1, 98.9, 100.4, 98.6, 101.4],
        d=0.5,
        k=3.0,
        precision_method="observed_sd_ratio_exploratory",
        allow_exploratory_precision_as_primary=False,
    )

    assert result["accuracy"]["pass"] is True
    assert result["precision"]["pass"] is True
    assert result["overall_pass"] is False
    assert result["precision_is_primary"] is False
    assert "exploratory observed-SD precision was not allowed" in result["decision_text"]
