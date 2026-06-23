import pytest

from nir_cp.statistics_usp1010 import (
    paired_precision_noninferiority_from_duplicate_measurements,
    paired_precision_noninferiority_known_old_variance,
    precision_noninferiority,
    precision_ratio_upper_bound,
)


def test_precision_noninferiority_passes_for_similar_variability() -> None:
    old = [100.0, 101.0, 99.0, 100.5, 98.5, 101.5]
    new = [100.1, 101.1, 98.9, 100.4, 98.6, 101.4]

    result = precision_noninferiority(old, new, k=3.0, alpha=0.05)

    assert result["pass"] is True
    assert result["ratio_observed"] == pytest.approx(1.0, rel=0.1)
    assert result["upper_bound"] < 3.0
    assert result["df_old"] == 5
    assert result["df_new"] == 5


def test_precision_noninferiority_fails_when_new_variability_is_much_larger() -> None:
    old = [100.0, 100.1, 99.9, 100.0, 100.05, 99.95]
    new = [96.0, 98.0, 100.0, 102.0, 104.0, 106.0]

    result = precision_noninferiority(old, new, k=2.0, alpha=0.05)

    assert result["pass"] is False
    assert result["ratio_observed"] > 2.0
    assert result["upper_bound"] > 2.0


def test_precision_ratio_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="matching paired lengths"):
        precision_ratio_upper_bound([1.0, 2.0, 3.0], [1.0, 2.0])


def test_precision_ratio_rejects_zero_old_sd() -> None:
    with pytest.raises(ValueError, match="standard deviation"):
        precision_ratio_upper_bound([10.0, 10.0, 10.0], [9.0, 10.0, 11.0])


def test_paired_precision_known_old_variance_passes() -> None:
    old = [100.0, 100.0, 100.0, 100.0, 100.0]
    new = [100.1, 99.9, 100.2, 99.8, 100.0]

    result = paired_precision_noninferiority_known_old_variance(
        old,
        new,
        old_variance=0.05,
        k=2.0,
    )

    assert result["pass"] is True
    assert result["method"] == "paired_known_old_variance"
    assert result["upper_bound"] < 2.0


def test_paired_precision_known_old_variance_negative_expression_raises() -> None:
    old = [100.0, 100.0, 100.0]
    new = [100.01, 100.02, 100.03]

    with pytest.raises(ValueError, match="square root"):
        paired_precision_noninferiority_known_old_variance(
            old,
            new,
            old_variance=100.0,
            k=2.0,
        )


def test_paired_precision_duplicate_measurements_passes() -> None:
    result = paired_precision_noninferiority_from_duplicate_measurements(
        old_rep1=[100.0, 100.3, 99.8, 100.2],
        old_rep2=[99.9, 100.1, 99.9, 100.0],
        new_rep1=[100.0, 100.2, 99.9, 100.2],
        new_rep2=[99.95, 100.05, 99.95, 100.05],
        k=3.0,
    )

    assert result["pass"] is True
    assert result["method"] == "paired_duplicate_measurements"
    assert result["upper_bound"] < 3.0


def test_paired_precision_duplicate_measurements_validates_inputs() -> None:
    with pytest.raises(ValueError, match="matching lengths"):
        paired_precision_noninferiority_from_duplicate_measurements(
            [1.0, 2.0],
            [1.0, 2.0],
            [1.0, 2.0, 3.0],
            [1.0, 2.0],
            k=2.0,
        )

    with pytest.raises(ValueError, match="old duplicate"):
        paired_precision_noninferiority_from_duplicate_measurements(
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [1.0, 1.1, 1.2],
            [1.0, 1.0, 1.0],
            k=2.0,
        )
