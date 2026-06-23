"""HTML table helpers for notebook reports."""

from __future__ import annotations

from numbers import Integral, Real

import pandas as pd


def _float_formatter(float_format: str):
    return lambda value: float_format.format(value)


def _format_transposed_value(value: object, float_format: str) -> object:
    if isinstance(value, Real) and not isinstance(value, (bool, Integral)):
        return float_format.format(value)
    return value


def format_report_dataframe(
    df: pd.DataFrame,
    max_rows: int | None = None,
    max_cols: int | None = None,
    float_format: str = "{:.3f}",
    index: bool = False,
    transpose_if_one_row: bool = False,
) -> str:
    """Format a dataframe as report-ready HTML without mutating the input."""

    display_df = df
    if max_rows is not None:
        display_df = display_df.head(max_rows)

    column_note = ""
    if max_cols is not None and len(display_df.columns) > max_cols:
        shown_columns = list(display_df.columns[:max_cols])
        display_df = display_df.loc[:, shown_columns]
        column_note = (
            '<p class="report-dataframe-note">'
            f"Showing first {max_cols} of {len(df.columns)} columns; not all columns are shown."
            "</p>"
        )

    if transpose_if_one_row and len(display_df) == 1:
        row = display_df.iloc[0]
        display_df = pd.DataFrame(
            {
                "parameter": [str(column) for column in row.index],
                "value": [
                    _format_transposed_value(value, float_format)
                    for value in row.to_list()
                ],
            }
        )
        index = False

    table_html = display_df.to_html(
        classes="report-dataframe",
        escape=True,
        float_format=_float_formatter(float_format),
        index=index,
    )
    return f"{column_note}{table_html}"


def display_report_dataframe(
    df: pd.DataFrame,
    max_rows: int | None = None,
    max_cols: int | None = None,
    float_format: str = "{:.3f}",
    index: bool = False,
    transpose_if_one_row: bool = False,
) -> str:
    """Display a report-ready dataframe table in IPython and return the HTML."""

    html = format_report_dataframe(
        df,
        max_rows=max_rows,
        max_cols=max_cols,
        float_format=float_format,
        index=index,
        transpose_if_one_row=transpose_if_one_row,
    )

    try:
        from IPython.display import HTML, display
    except ImportError:
        return html

    display(HTML(html))
    return html
