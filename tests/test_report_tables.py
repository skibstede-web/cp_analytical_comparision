import pandas as pd

from nir_cp.report_tables import display_report_dataframe, format_report_dataframe


def test_format_report_dataframe_returns_html_string() -> None:
    df = pd.DataFrame({"sample_id": ["S1"], "value": [1.23456]})

    html = format_report_dataframe(df)

    assert isinstance(html, str)
    assert "<table" in html
    assert "1.235" in html


def test_format_report_dataframe_applies_float_format() -> None:
    df = pd.DataFrame({"sample_id": ["S1"], "alpha": [0.05], "value": [1.23456]})

    html = format_report_dataframe(df, float_format="{:.2f}")

    assert "0.05" in html
    assert "1.23" in html
    assert "1.23456" not in html


def test_format_report_dataframe_includes_report_dataframe_class() -> None:
    df = pd.DataFrame({"sample_id": ["S1"], "value": [1.0]})

    html = format_report_dataframe(df)

    assert "report-dataframe" in html


def test_format_report_dataframe_does_not_mutate_input_dataframe() -> None:
    df = pd.DataFrame(
        {
            "sample_id": ["S1", "S2"],
            "value": [1.0, 2.0],
            "extra": ["alpha", "beta"],
        }
    )
    original = df.copy(deep=True)

    format_report_dataframe(df, max_rows=1, max_cols=2)

    pd.testing.assert_frame_equal(df, original)


def test_format_report_dataframe_transposes_one_row_dataframe() -> None:
    df = pd.DataFrame(
        [
            {
                "alpha_accuracy": 0.05,
                "n_simulations": 500,
                "probability_of_success": 0.875,
            }
        ]
    )

    html = format_report_dataframe(
        df,
        float_format="{:.2f}",
        transpose_if_one_row=True,
    )

    assert "<th>parameter</th>" in html
    assert "<th>value</th>" in html
    assert "<td>alpha_accuracy</td>" in html
    assert "<td>0.05</td>" in html
    assert "<td>probability_of_success</td>" in html
    assert "<td>0.88</td>" in html


def test_format_report_dataframe_preserves_intact_numeric_strings() -> None:
    df = pd.DataFrame({"alpha": [0.05]})

    html = format_report_dataframe(df, float_format="{:.2f}")

    assert "<td>0.05</td>" in html
    assert "0.0</td>" not in html


def test_format_report_dataframe_max_cols_adds_explanatory_note() -> None:
    df = pd.DataFrame({"a": [1], "b": [2], "c": [3]})

    html = format_report_dataframe(df, max_cols=2)

    assert "not all columns are shown" in html
    assert "first 2 of 3 columns" in html
    assert "<th>b</th>" in html
    assert "<th>c</th>" not in html


def test_display_report_dataframe_returns_html_string() -> None:
    df = pd.DataFrame({"sample_id": ["S1"], "value": [1.0]})

    html = display_report_dataframe(df)

    assert isinstance(html, str)
    assert "report-dataframe" in html


def test_display_report_dataframe_passes_through_transpose_option() -> None:
    df = pd.DataFrame([{"alpha_accuracy": 0.05, "n_simulations": 500}])

    html = display_report_dataframe(
        df,
        float_format="{:.2f}",
        transpose_if_one_row=True,
    )

    assert "<th>parameter</th>" in html
    assert "<td>alpha_accuracy</td>" in html
    assert "<td>0.05</td>" in html
