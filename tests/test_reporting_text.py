from nir_cp.reporting_text import paired_decision_summary_text


def _decision_result(overall_pass: bool) -> dict[str, object]:
    return {
        "overall_pass": overall_pass,
        "accuracy": {
            "pass": overall_pass,
            "mean_difference": 0.1234,
            "ci_confidence": 0.90,
            "lower": -0.2345,
            "upper": 0.4567,
            "d": 0.5,
        },
        "precision": {
            "pass": overall_pass,
            "upper_bound": 1.6789,
            "k": 2.0,
        },
    }


def test_paired_decision_summary_text_includes_pass_wording_and_values() -> None:
    text = paired_decision_summary_text(_decision_result(True), method_name="Test NIR")

    assert "Test NIR met the predefined criteria" in text
    assert "0.123" in text
    assert "-0.234" in text
    assert "0.457" in text
    assert "+/-0.500" in text
    assert "1.679" in text
    assert "k=2.000" in text


def test_paired_decision_summary_text_includes_fail_wording() -> None:
    text = paired_decision_summary_text(_decision_result(False), method_name="Test NIR")

    assert "Test NIR did not meet the predefined criteria" in text
    assert "met the predefined criteria for paired accuracy" not in text
