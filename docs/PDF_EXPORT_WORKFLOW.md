# PDF Export Workflow

Notebook report export is implemented in `src/nir_cp/notebook_export.py`.

## HTML Export

1. Author analyses as notebooks in `notebooks/`.
2. Execute notebooks with project functions imported from `src/nir_cp/`.
3. Read notebook JSON with `_read_export_notebook`, which sanitizes volatile export metadata and validates the notebook with `nbformat`.
4. Convert the notebook to HTML with `nbconvert.HTMLExporter`.
5. Optionally hide code cells, input prompts, output prompts, and raw cells for report output.
6. Inject project `PRINT_CSS` into the HTML head for A4 landscape print styling, readable fonts, clean tables, and page-break behavior.
7. Write generated HTML to `reports/html/` or another selected output path.

## PDF Export

`export_notebook_pdf` first creates styled HTML next to the requested PDF target, then prints that HTML to PDF using a headless Chrome, Edge, or Chromium browser. The default page layout is A4 landscape to preserve wide tabular notebook output. Use portrait pages only for reports known to fit portrait pages.

Browser discovery checks an explicit `browser_path` first when provided, then common executable names and Windows install paths for Edge, Chrome, and Chromium. If no browser is available, PDF export raises a runtime error.

The browser is called with a temporary user-data directory and headless print flags, including `--print-to-pdf=<pdf_path>`. PDF export also uses a short Chrome/Edge virtual-time budget and a MathJax readiness hook in the HTML so LaTeX equations have time to typeset before printing. The function verifies that a non-empty PDF was created. Intermediate HTML can be retained for review or deleted with `keep_html=False`.

Generated reports are ignored by Git. Commit only notebooks, source code, tests, curated summaries, and documentation.

## Report-visible theory sections

The report notebooks include markdown `Statistical theory and decision rules` sections with short explanatory text, equations, hypotheses, and generated `Values used in this notebook` tables. These sections are intended to remain visible in clean PDF exports when `hide_code=True`; code cells may be hidden, but theory, equations, values tables, results, plots, and final decision text should remain visible.

Equations in notebook report sections are rendered as inline SVG outputs with `nir_cp.report_equations.display_equation(...)` or `display_equation_set(...)`. These helpers use Matplotlib mathtext, so report equations do not depend on MathJax, internet access, or an external LaTeX installation. Notebook code cells may generate visible equation outputs while code input is hidden in clean PDFs with `hide_code=True`.

Do not author report-visible theory equations as raw Markdown math blocks. Spaced delimiters such as `$ $` are invalid, and raw `$$ ... $$` blocks can print as literal text when MathJax is unavailable or does not finish before browser PDF printing. The text is a concise project paraphrase and does not reproduce long USP <1010> source text. Values tables should be rendered with `display_report_dataframe(...)`, using `transpose_if_one_row=True` for compact one-row configuration or simulation dictionaries.

## Wide Table Strategy

Notebook export CSS targets pandas and Jupyter-rendered HTML tables, including `.dataframe`, `table.dataframe`, `table.report-dataframe`, `.jp-RenderedHTMLCommon table`, and `.rendered_html table`. Tables are allowed to use the full page width and print overflow is forced visible so browser print containers do not clip the right side.

Headers may wrap aggressively to keep columns compact. Data cells are kept on one line with tabular numerals so numeric values such as `0.05` are not split across PDF line breaks. This favors readable compact values over forcing every wide result table into a single horizontal row.

Use `nir_cp.report_tables.display_report_dataframe(...)` for report-facing dataframe output, especially wide raw-data previews. Raw input previews should usually be limited with `max_rows=10` and, when needed, `max_cols=<n>` so reports show enough traceable context without overwhelming the PDF. For one-row simulation results or wide result dictionaries, use `transpose_if_one_row=True` to render a two-column `parameter`/`value` table while preserving all scientific result values.
