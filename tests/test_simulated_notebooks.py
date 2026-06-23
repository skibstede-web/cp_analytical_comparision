from pathlib import Path

import nbformat


SIMULATED_NOTEBOOKS = [
    Path("notebooks/01_general_paired_offline_nir_comparison_simulated.ipynb"),
    Path("notebooks/02_granule_assay_paired_comparison_simulated.ipynb"),
    Path("notebooks/03_tablet_transmission_paired_comparison_simulated.ipynb"),
    Path("notebooks/04_inline_diversion_performance_verification_simulated.ipynb"),
]

REQUIRED_CONFIG_VARIABLES = [
    "D_EQUIVALENCE_MARGIN",
    "K_PRECISION_RATIO",
    "ALPHA_ACCURACY",
    "ALPHA_PRECISION",
    "RECOMMENDED_MIN_N",
    "OLD_MEAN",
    "OLD_SD",
    "NEW_MEAN",
    "NEW_SD",
]


def _read_notebook(path: Path) -> nbformat.NotebookNode:
    return nbformat.read(path, as_version=4)


def _combined_source(notebook: nbformat.NotebookNode) -> str:
    return "\n".join(str(cell.source) for cell in notebook.cells)


def test_simulated_notebooks_exist_and_open() -> None:
    for path in SIMULATED_NOTEBOOKS:
        assert path.exists(), f"Missing simulated notebook: {path}"
        notebook = _read_notebook(path)
        assert notebook.nbformat == 4


def test_simulated_notebooks_have_user_configuration_cells() -> None:
    for path in SIMULATED_NOTEBOOKS:
        notebook = _read_notebook(path)
        config_cells = [
            cell
            for cell in notebook.cells
            if cell.cell_type == "code" and "USER CONFIGURATION" in str(cell.source)
        ]
        assert config_cells, f"{path} is missing a USER CONFIGURATION code cell"
        config_source = str(config_cells[0].source)
        for variable in REQUIRED_CONFIG_VARIABLES:
            assert variable in config_source, f"{path} config missing {variable}"


def test_simulated_notebooks_have_data_simulation_cells() -> None:
    for path in SIMULATED_NOTEBOOKS:
        notebook = _read_notebook(path)
        assert any(
            cell.cell_type == "code" and "simulate_" in str(cell.source)
            for cell in notebook.cells
        ), f"{path} is missing a code cell that simulates data"


def test_simulated_notebooks_default_to_no_pdf_export() -> None:
    for path in SIMULATED_NOTEBOOKS:
        combined = _combined_source(_read_notebook(path))
        assert "EXPORT_REPORT = False" in combined, f"{path} should not export by default"


def test_tablet_simulated_notebook_has_no_orientation_text() -> None:
    tablet_path = Path("notebooks/03_tablet_transmission_paired_comparison_simulated.ipynb")
    combined = _combined_source(_read_notebook(tablet_path))

    assert "orientation" not in combined.lower()
