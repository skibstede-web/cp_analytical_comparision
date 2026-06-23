import pytest

from nir_cp.report_equations import (
    display_equation,
    display_equation_set,
    equation_svg_html,
)


def test_equation_svg_html_returns_inline_svg() -> None:
    html = equation_svg_html(r"H_0: |\mu_D| \ge d")

    assert isinstance(html, str)
    assert "<svg" in html
    assert "report-equation" in html


def test_display_equation_returns_html_string() -> None:
    html = display_equation(r"D_i = Y_{N,i} - Y_{O,i}")

    assert isinstance(html, str)
    assert "<svg" in html


def test_display_equation_set_returns_html_strings() -> None:
    html_values = display_equation_set(
        [
            r"H_0: |\mu_D| \ge d",
            r"H_A: |\mu_D| < d",
        ]
    )

    assert len(html_values) == 2
    assert all(isinstance(value, str) for value in html_values)
    assert all("<svg" in value for value in html_values)


@pytest.mark.parametrize("latex", ["", "   ", r"\notacommand{x}"])
def test_equation_svg_html_rejects_invalid_or_empty_input(latex: str) -> None:
    with pytest.raises(ValueError):
        equation_svg_html(latex)
