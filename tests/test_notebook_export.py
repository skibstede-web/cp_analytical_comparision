import re
from pathlib import Path

import nbformat
import pytest

from nir_cp.notebook_export import (
    MATHJAX_PRINT_WAIT_SCRIPT,
    PRINT_CSS,
    _find_browser,
    _read_export_notebook,
    export_notebook_html,
    export_notebook_pdf,
)


def _write_minimal_notebook(path: Path) -> Path:
    notebook = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell("# Export Test"),
            nbformat.v4.new_code_cell("print('hello export')"),
        ],
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12"},
            "widgets": {"application/vnd.jupyter.widget-state+json": {}},
        },
    )
    path.write_text(nbformat.writes(notebook), encoding="utf-8")
    return path


def test_read_export_notebook_reads_valid_notebook(tmp_path: Path) -> None:
    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")

    notebook = _read_export_notebook(notebook_path)

    assert notebook.nbformat == 4
    assert len(notebook.cells) == 2
    assert "widgets" not in notebook.metadata


def test_export_notebook_html_creates_html_with_print_css(tmp_path: Path) -> None:
    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")
    html_path = tmp_path / "report.html"

    result = export_notebook_html(notebook_path, html_path)

    assert result == html_path
    html = html_path.read_text(encoding="utf-8")
    assert "@page" in html
    assert "A4 landscape" in html
    assert PRINT_CSS.strip() in html
    assert MATHJAX_PRINT_WAIT_SCRIPT.strip() in html
    assert "Export Test" in html


def test_export_notebook_html_includes_dataframe_print_css(tmp_path: Path) -> None:
    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")
    html_path = tmp_path / "report.html"

    export_notebook_html(notebook_path, html_path)

    html = html_path.read_text(encoding="utf-8")
    assert "table.dataframe" in html
    assert "table.report-dataframe" in html
    assert ".jp-RenderedHTMLCommon table" in html
    assert ".rendered_html table" in html
    assert "overflow-wrap: anywhere" in html
    assert ".output_html" in html


def test_export_notebook_html_keeps_numeric_table_cells_unbroken(
    tmp_path: Path,
) -> None:
    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")
    html_path = tmp_path / "report.html"

    export_notebook_html(notebook_path, html_path)

    html = html_path.read_text(encoding="utf-8")
    assert "td,\n.report-dataframe td {\n  white-space: nowrap;" in html
    assert "font-variant-numeric: tabular-nums;" in html
    assert not re.search(r"td[^{]*\{[^}]*overflow-wrap:\s*anywhere", html)


def test_export_notebook_html_allows_table_headers_to_wrap(tmp_path: Path) -> None:
    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")
    html_path = tmp_path / "report.html"

    export_notebook_html(notebook_path, html_path)

    html = html_path.read_text(encoding="utf-8")
    assert "th,\n.report-dataframe th {\n  white-space: normal;" in html
    assert "th,\n.report-dataframe th {\n  white-space: normal;\n  overflow-wrap: anywhere;" in html
    assert "word-break: normal;" in html


def test_export_notebook_html_accepts_portrait_orientation(tmp_path: Path) -> None:
    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")
    html_path = tmp_path / "report.html"

    export_notebook_html(notebook_path, html_path, page_orientation="portrait")

    html = html_path.read_text(encoding="utf-8")
    assert "A4 portrait" in html
    assert "A4 landscape" not in html


def test_export_notebook_html_rejects_invalid_orientation(tmp_path: Path) -> None:
    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")
    html_path = tmp_path / "report.html"

    with pytest.raises(ValueError, match="page_orientation"):
        export_notebook_html(notebook_path, html_path, page_orientation="square")


def test_read_export_notebook_missing_path_raises_file_not_found(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileNotFoundError):
        _read_export_notebook(tmp_path / "missing.ipynb")


def test_read_export_notebook_invalid_json_raises_value_error(tmp_path: Path) -> None:
    notebook_path = tmp_path / "invalid.ipynb"
    notebook_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="not valid notebook JSON"):
        _read_export_notebook(notebook_path)


def test_find_browser_prefers_existing_explicit_path(tmp_path: Path) -> None:
    fake_browser = tmp_path / "fake-browser.exe"
    fake_browser.write_text("", encoding="utf-8")

    assert _find_browser(preferred=fake_browser) == str(fake_browser)


def test_export_notebook_pdf_creates_non_empty_pdf_when_browser_is_available(
    tmp_path: Path,
) -> None:
    try:
        browser = _find_browser()
    except RuntimeError:
        pytest.skip("No Chrome, Edge, or Chromium browser available for PDF export.")

    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")
    pdf_path = tmp_path / "report.pdf"

    result = export_notebook_pdf(
        notebook_path,
        pdf_path,
        browser_path=browser,
        keep_html=False,
    )

    assert result == pdf_path
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert not pdf_path.with_suffix(".html").exists()


def test_mathjax_wait_script_marks_exported_html(tmp_path: Path) -> None:
    notebook_path = _write_minimal_notebook(tmp_path / "minimal.ipynb")
    html_path = tmp_path / "report.html"

    export_notebook_html(notebook_path, html_path)

    html = html_path.read_text(encoding="utf-8")
    assert 'data-mathjax-ready", "true"' in html
    assert "window.MathJax.Hub.Queue" in html
