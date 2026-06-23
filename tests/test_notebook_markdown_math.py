import re
from pathlib import Path

import nbformat


PAIRED_NOTEBOOKS = [
    Path("notebooks/01_general_paired_offline_nir_comparison.ipynb"),
    Path("notebooks/02_granule_assay_paired_comparison.ipynb"),
    Path("notebooks/03_tablet_transmission_paired_comparison.ipynb"),
]

INLINE_NOTEBOOK = Path("notebooks/04_inline_diversion_performance_verification.ipynb")
ALL_NOTEBOOKS = [*PAIRED_NOTEBOOKS, INLINE_NOTEBOOK]

FORBIDDEN_MARKDOWN_PATTERNS = {
    "$ $": re.escape("$ $"),
    "$  $": re.escape("$  $"),
    "D_bar": r"(?<!\\)D_bar",
    "mu_D": r"(?<!\\)mu_D",
    "sqrt(n)": re.escape("sqrt(n)"),
    "sum(D_i": re.escape("sum(D_i"),
}


def _markdown_sources(path: Path) -> list[str]:
    notebook = nbformat.read(path, as_version=4)
    return [
        str(cell.source)
        for cell in notebook.cells
        if cell.cell_type == "markdown"
    ]


def test_notebook_markdown_uses_valid_display_math_delimiters() -> None:
    for path in ALL_NOTEBOOKS:
        combined = "\n".join(_markdown_sources(path))

        assert "# Statistical theory and decision rules" in combined, (
            f"{path} is missing the notebook-visible theory section"
        )
        assert combined.count("$$") >= 2, (
            f"{path} is missing a valid display math delimiter pair"
        )

        for token, pattern in FORBIDDEN_MARKDOWN_PATTERNS.items():
            assert not re.search(pattern, combined), (
                f"{path} contains invalid math token {token!r}"
            )


def test_paired_notebooks_include_required_latex_symbols() -> None:
    required_tokens = [
        r"\mu_D",
        r"\bar{D}",
        r"\sigma_N",
    ]

    for path in PAIRED_NOTEBOOKS:
        combined = "\n".join(_markdown_sources(path))
        for token in required_tokens:
            assert token in combined, f"{path} missing {token!r}"


def test_inline_notebook_includes_required_latex_symbols() -> None:
    combined = "\n".join(_markdown_sources(INLINE_NOTEBOOK))

    for token in ["Y_{NIR,i}", "RMSEP", r"\beta_0"]:
        assert token in combined, f"{INLINE_NOTEBOOK} missing {token!r}"
