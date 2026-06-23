import json
from pathlib import Path


PAIRED_NOTEBOOKS = [
    Path("notebooks/01_general_paired_offline_nir_comparison.ipynb"),
    Path("notebooks/02_granule_assay_paired_comparison.ipynb"),
    Path("notebooks/03_tablet_transmission_paired_comparison.ipynb"),
]

INLINE_NOTEBOOK = Path("notebooks/04_inline_diversion_performance_verification.ipynb")


def _cell_sources(path: Path) -> list[str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return ["".join(cell.get("source", "")) for cell in notebook["cells"]]


def test_paired_notebooks_include_visible_theory_sections() -> None:
    required_text = [
        "# Statistical theory and decision rules",
        "## Study design",
        "## Accuracy equivalence",
        "## Precision noninferiority",
        "## Values used in this notebook",
        "H_0: |\\mu_D| \\ge d",
        "H_A: |\\mu_D| < d",
        "\\bar{D} = \\frac{1}{n}\\sum_{i=1}^{n}D_i",
        "\\frac{\\sigma_N}{\\sigma_O}",
        "\\chi^2_{\\alpha,n-1}",
        "d_{O,i} = \\frac{Y_{O,i,1}-Y_{O,i,2}}{\\sqrt{2}}",
        "Precision method note: the observed SD-ratio calculation shown in this example",
        "tested functions under `src/nir_cp/`",
    ]

    for path in PAIRED_NOTEBOOKS:
        combined = "\n".join(_cell_sources(path))
        for expected in required_text:
            assert expected in combined, f"{path} missing {expected!r}"
        assert "display_report_dataframe(pd.DataFrame([values_used]), transpose_if_one_row=True)" in combined


def test_inline_notebook_includes_visible_theory_section() -> None:
    combined = "\n".join(_cell_sources(INLINE_NOTEBOOK))
    required_text = [
        "# Statistical theory and decision rules",
        "## Study design",
        "## Accuracy versus reference",
        "## Diversion-zone assessment",
        "## process_repeatability by local linear detrending",
        "## Values used in this notebook",
        "e_i = Y_{NIR,i} - Y_{REF,i}",
        "RMSEP = \\sqrt{\\frac{1}{n}\\sum_{i=1}^{n}e_i^2}",
        "Y_{NIR,i} < L_{div}",
        "s_r = \\sqrt",
        "tested functions under `src/nir_cp/`",
        "display_report_dataframe(pd.DataFrame([values_used]), transpose_if_one_row=True)",
    ]

    for expected in required_text:
        assert expected in combined, f"{INLINE_NOTEBOOK} missing {expected!r}"
