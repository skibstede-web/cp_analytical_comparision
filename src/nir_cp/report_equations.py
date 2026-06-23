"""Report-facing equation rendering helpers."""

from __future__ import annotations

import re
from io import BytesIO

import matplotlib

matplotlib.use("Agg", force=True)

from matplotlib import pyplot as plt  # noqa: E402


def _normalize_mathtext(latex: str) -> str:
    return latex.replace(r"\ge", r"\geq").replace(r"\le", r"\leq")


def equation_svg_html(latex: str, fontsize: int = 15) -> str:
    """Render a mathtext expression as inline SVG HTML.

    Parameters
    ----------
    latex:
        LaTeX math expression without surrounding ``$`` or ``$$`` delimiters.
    fontsize:
        Matplotlib font size used for the rendered equation.
    """

    if not isinstance(latex, str) or not latex.strip():
        raise ValueError("latex must be a non-empty string")
    if fontsize <= 0:
        raise ValueError("fontsize must be positive")

    expression = latex.strip()
    mathtext_expression = _normalize_mathtext(expression)
    figure = plt.figure(figsize=(0.01, 0.01))
    figure.patch.set_alpha(0)

    try:
        figure.text(0, 0, f"${mathtext_expression}$", fontsize=fontsize)
        buffer = BytesIO()
        figure.savefig(
            buffer,
            format="svg",
            bbox_inches="tight",
            pad_inches=0.04,
            transparent=True,
        )
    except Exception as exc:
        raise ValueError(f"Could not render equation: {expression}") from exc
    finally:
        plt.close(figure)

    svg = buffer.getvalue().decode("utf-8")
    svg_start = svg.find("<svg")
    if svg_start == -1:
        raise ValueError(f"Could not render equation: {expression}")
    svg = svg[svg_start:]
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.DOTALL)

    return (
        '<div class="report-equation" '
        'style="margin: 0.55rem 0; overflow: visible;">'
        '<style>'
        ".report-equation svg { max-width: 100%; height: auto; overflow: visible; }"
        "</style>"
        f"{svg}"
        "</div>"
    )


def display_equation(latex: str, fontsize: int = 15) -> str:
    """Display a rendered equation in IPython and return its HTML."""

    html = equation_svg_html(latex, fontsize=fontsize)
    try:
        from IPython.display import HTML, display
    except ImportError:
        return html

    display(HTML(html))
    return html


def display_equation_set(equations: list[str], fontsize: int = 15) -> list[str]:
    """Display a sequence of rendered equations and return their HTML strings."""

    return [display_equation(equation, fontsize=fontsize) for equation in equations]
