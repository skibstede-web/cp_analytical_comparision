import pytest

from nir_cp.statistics_usp1010 import mean_ci_t, paired_accuracy_equivalence


def test_mean_ci_t_returns_expected_keys() -> None:
    result = mean_ci_t([1.0, 2.0, 3.0, 4.0], confidence=0.90)

    assert result["n"] == 4
    assert result["mean"] == pytest.approx(2.5)
    assert result["sd"] == pytest.approx(1.2909944487)
    assert result["se"] == pytest.approx(0.6454972244)
    assert result["confidence"] == pytest.approx(0.90)
    assert result["lower"] < result["mean"] < result["upper"]


def test_paired_accuracy_passes_when_methods_are_nearly_identical() -> None:
    old = [100.0, 101.2, 99.5, 100.8, 98.9, 101.0]
    new = [100.1, 101.1, 99.6, 100.7, 99.0, 101.1]

    result = paired_accuracy_equivalence(old, new, d=0.5, alpha=0.05)

    assert result["pass"] is True
    assert result["n"] == 6
    assert result["ci_confidence"] == pytest.approx(0.90)
    assert -0.5 <= result["lower"] <= result["upper"] <= 0.5


def test_paired_accuracy_fails_when_mean_difference_exceeds_margin() -> None:
    old = [100.0, 101.0, 99.0, 100.5, 98.5, 101.5]
    new = [101.2, 102.2, 100.2, 101.7, 99.7, 102.7]

    result = paired_accuracy_equivalence(old, new, d=0.5, alpha=0.05)

    assert result["pass"] is False
    assert result["mean_difference"] == pytest.approx(1.2)
    assert result["lower"] > 0.5


def test_paired_accuracy_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="matching paired lengths"):
        paired_accuracy_equivalence([1.0, 2.0, 3.0], [1.0, 2.0], d=0.5)


def test_mean_ci_t_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError, match="finite"):
        mean_ci_t([1.0, float("nan"), 3.0])
