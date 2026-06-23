"""Notebook export utilities for HTML and PDF report generation."""

from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from nbformat import NotebookNode
from traitlets.config import Config


PRINT_CSS = """
<style>
@page {
  size: A4 landscape;
  margin: 10mm;
}

html,
body {
  color: #1f2933;
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.45;
}

body {
  max-width: none;
  margin: 0 auto;
  padding: 18px 28px;
  background: #ffffff;
}

h1,
h2,
h3,
h4 {
  color: #111827;
  font-weight: 650;
  line-height: 1.2;
  page-break-after: avoid;
  break-after: avoid;
}

h1 {
  border-bottom: 2px solid #d1d5db;
  padding-bottom: 0.35em;
}

table {
  border-collapse: collapse;
  width: 100%;
  max-width: 100%;
  margin: 1em 0;
  page-break-inside: avoid;
  break-inside: avoid;
}

.dataframe,
table.dataframe,
table.report-dataframe,
.jp-RenderedHTMLCommon table,
.rendered_html table {
  border-collapse: collapse;
  width: 100%;
  max-width: 100%;
  table-layout: auto;
  font-size: 8pt;
}

th,
td {
  border: 1px solid #d1d5db;
  padding: 3px 5px;
  vertical-align: top;
}

th,
.report-dataframe th {
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: normal;
}

td,
.report-dataframe td {
  white-space: nowrap;
  word-break: normal;
  overflow-wrap: normal;
  font-variant-numeric: tabular-nums;
}

th {
  background: #f3f4f6;
  font-weight: 650;
}

.report-dataframe-note {
  color: #4b5563;
  font-size: 8pt;
  margin: 0.4em 0 0.8em;
}

tr {
  page-break-inside: avoid;
  break-inside: avoid;
}

pre,
code {
  font-family: "Cascadia Mono", Consolas, monospace;
  font-size: 9.5pt;
}

pre {
  white-space: pre-wrap;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 0.8em;
  background: #f9fafb;
  page-break-inside: avoid;
  break-inside: avoid;
}

img,
svg {
  max-width: 100%;
  height: auto;
  page-break-inside: avoid;
  break-inside: avoid;
}

canvas {
  max-width: 100%;
  height: auto;
  page-break-inside: avoid;
  break-inside: avoid;
}

.jp-RenderedHTMLCommon,
.jp-OutputArea-output {
  overflow-wrap: normal;
}

.jp-Cell,
.cell {
  page-break-inside: avoid;
  break-inside: avoid;
}

@media print {
  * {
    overflow: visible !important;
  }

  body {
    max-width: none;
    margin: 0;
    padding: 0;
  }

  .jp-OutputArea-output,
  .output_html,
  .output_subarea {
    overflow: visible !important;
    max-width: 100% !important;
  }

  a {
    color: #111827;
    text-decoration: none;
  }
}
</style>
"""


MATHJAX_PRINT_WAIT_SCRIPT = """
<script>
(function () {
  function markReady() {
    document.documentElement.setAttribute("data-mathjax-ready", "true");
  }

  if (window.MathJax && window.MathJax.Hub) {
    window.MathJax.Hub.Queue(["Typeset", window.MathJax.Hub], markReady);
  } else {
    window.setTimeout(markReady, 3000);
  }
})();
</script>
"""


def _print_css(page_orientation: str) -> str:
    """Return print CSS for the requested page orientation."""

    normalized_orientation = page_orientation.lower()
    if normalized_orientation not in {"landscape", "portrait"}:
        raise ValueError("page_orientation must be 'landscape' or 'portrait'.")
    if normalized_orientation == "landscape":
        return PRINT_CSS
    return PRINT_CSS.replace("A4 landscape", "A4 portrait", 1)


def _read_export_notebook(notebook_path: str | os.PathLike[str]) -> NotebookNode:
    """Read, sanitize, and validate a notebook for export."""

    path = Path(notebook_path)
    if not path.exists():
        raise FileNotFoundError(path)

    try:
        with path.open("r", encoding="utf-8") as handle:
            raw_notebook = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid notebook JSON.") from exc

    if not isinstance(raw_notebook, dict):
        raise ValueError(f"{path} is not a valid notebook.")
    if "cells" not in raw_notebook or "nbformat" not in raw_notebook:
        raise ValueError(f"{path} is not a valid notebook.")

    notebook_dict = copy.deepcopy(raw_notebook)
    metadata = notebook_dict.setdefault("metadata", {})
    if isinstance(metadata, dict):
        for key in ("widgets", "signature"):
            metadata.pop(key, None)

    for cell in notebook_dict.get("cells", []):
        if not isinstance(cell, dict):
            continue
        if isinstance(cell.get("source"), list):
            cell["source"] = "".join(cell["source"])
        cell_metadata = cell.setdefault("metadata", {})
        if isinstance(cell_metadata, dict):
            for key in ("execution", "ExecuteTime"):
                cell_metadata.pop(key, None)
        for output in cell.get("outputs", []):
            if not isinstance(output, dict):
                continue
            if isinstance(output.get("text"), list):
                output["text"] = "".join(output["text"])
            data = output.get("data", {})
            if isinstance(data, dict):
                for mime_type, value in list(data.items()):
                    if isinstance(value, list):
                        data[mime_type] = "".join(value)

    try:
        notebook = nbformat.from_dict(notebook_dict)
        nbformat.validate(notebook)
    except Exception as exc:
        raise ValueError(f"{path} is not a valid notebook.") from exc

    return notebook


def _find_browser(preferred: str | os.PathLike[str] | None = None) -> str:
    """Find a Chrome, Edge, or Chromium executable."""

    checked: list[str] = []

    def add_candidate(candidate: str | os.PathLike[str] | None) -> None:
        if candidate is not None:
            text = str(candidate)
            if text and text not in checked:
                checked.append(text)

    add_candidate(preferred)

    names = [
        "msedge",
        "msedge.exe",
        "chrome",
        "chrome.exe",
        "chromium",
        "chromium.exe",
        "google-chrome",
        "google-chrome.exe",
    ]

    for name in names:
        add_candidate(name)

    program_files = [
        os.environ.get("PROGRAMFILES"),
        os.environ.get("PROGRAMFILES(X86)"),
        os.environ.get("LOCALAPPDATA"),
    ]
    browser_paths = [
        ("Microsoft", "Edge", "Application", "msedge.exe"),
        ("Google", "Chrome", "Application", "chrome.exe"),
        ("Chromium", "Application", "chromium.exe"),
    ]
    for root in program_files:
        if root:
            for parts in browser_paths:
                add_candidate(Path(root, *parts))

    for candidate in checked:
        candidate_path = Path(candidate).expanduser()
        if candidate_path.is_file():
            return str(candidate_path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    raise RuntimeError("No Chrome, Edge, or Chromium browser executable was found.")


def export_notebook_html(
    notebook_path: str | os.PathLike[str],
    html_path: str | os.PathLike[str],
    hide_code: bool = True,
    template_name: str = "lab",
    page_orientation: str = "landscape",
) -> Path:
    """Export a notebook to styled HTML."""

    notebook = _read_export_notebook(notebook_path)
    output_path = Path(html_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    config = Config()
    for section in (config.HTMLExporter, config.TemplateExporter):
        section.exclude_input = hide_code
        section.exclude_input_prompt = hide_code
        section.exclude_output_prompt = hide_code
        section.exclude_raw = hide_code

    exporter = HTMLExporter(config=config)
    exporter.template_name = template_name
    body, _resources = exporter.from_notebook_node(notebook)
    print_css = _print_css(page_orientation)

    if "</head>" in body:
        body = body.replace("</head>", f"{print_css}\n</head>", 1)
    else:
        body = f"{print_css}\n{body}"

    if "</body>" in body:
        body = body.replace("</body>", f"{MATHJAX_PRINT_WAIT_SCRIPT}\n</body>", 1)
    else:
        body = f"{body}\n{MATHJAX_PRINT_WAIT_SCRIPT}"

    output_path.write_text(body, encoding="utf-8")
    return output_path


def export_notebook_pdf(
    notebook_path: str | os.PathLike[str],
    pdf_path: str | os.PathLike[str],
    hide_code: bool = True,
    browser_path: str | os.PathLike[str] | None = None,
    keep_html: bool = True,
    page_orientation: str = "landscape",
) -> Path:
    """Export a notebook to PDF through intermediate HTML and headless browser print."""

    output_path = Path(pdf_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = output_path.with_suffix(".html")
    export_notebook_html(
        notebook_path,
        html_path,
        hide_code=hide_code,
        page_orientation=page_orientation,
    )

    browser = _find_browser(browser_path)
    html_uri = html_path.resolve().as_uri()

    with tempfile.TemporaryDirectory() as tempdir:
        subprocess.run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--virtual-time-budget=5000",
                f"--user-data-dir={tempdir}",
                f"--print-to-pdf={str(output_path.resolve())}",
                html_uri,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError(f"PDF export did not create a non-empty file: {output_path}")

    if not keep_html:
        html_path.unlink(missing_ok=True)

    return output_path
