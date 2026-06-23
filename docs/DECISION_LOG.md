# Decision Log

## 2026-06-23

Initial scaffold decision: the project is UV-managed, Python 3.12-only, notebook-first, and uses tested helper functions in `src/nir_cp/` for safety-critical statistical behavior.

Implemented the first paired off-line NIR statistical core for Granule Assay NIR and Tablet Transmission NIR cases where the same physical sample or tablet can be measured by both old and changed methods. The milestone adds paired accuracy equivalence using a Student t confidence interval on `new - old` differences, precision noninferiority using an F-distribution upper confidence bound for `sigma_new / sigma_old`, and a combined paired comparison decision wrapper with focused tests.

Added a probability-of-success simulation engine for paired off-line NIR comparative study planning. The milestone adds reproducible old/new data simulation, repeated paired comparison decision simulation, and sample-size scenario grids for Granule Assay NIR and Tablet Transmission NIR planning notebooks.

Implemented the notebook export utility for report generation. The milestone adds validated notebook JSON reading, nbconvert-based styled HTML export with project print CSS, optional headless Chrome/Edge/Chromium PDF export, browser discovery, and tests that exercise HTML export while conditionally testing PDF export when a compatible browser is available.

Created the first user-facing paired off-line NIR comparison notebook with synthetic example data for Granule Assay NIR and Tablet Transmission NIR. The milestone adds reusable plotting helpers, regulatory-style decision summary text, and a report-like notebook that calls tested statistical, simulation, and export utilities from `src/nir_cp/`.

Added method-specific placeholder configuration and specialized paired off-line NIR notebooks for Off-line Granule Assay NIR and Off-line Tablet Transmission NIR. The milestone adds YAML defaults marked as examples only, a validated method configuration loader, synthetic method-specific datasets, and notebooks that map the paired comparison workflow to granule presentation/refill considerations and tablet transmission path considerations.

Configured automated tests to force Matplotlib's non-interactive `Agg` backend through `tests/conftest.py`, avoiding GUI/Tk dependency failures in headless or broken-Tk environments while keeping production plotting modules notebook-interactive.

Added the first inline NIR diversion-control performance verification workflow. The milestone adds synthetic historical and prospective inline example data, reference-error and diversion-zone helpers, spectral diagnostic summaries, comparison of a new run against historical precomputed process_repeatability, an explicit placeholder for the company-specific process_repeatability algorithm, preliminary inline decision text, and a notebook workflow for inline diversion-control verification.

Hardened repository sharing and future agentic coding guidance. The milestone expands the README, adds review and regulatory resource handling checklists, updates project memory and USP <1010> traceability, and adds documentation presence tests so safety-critical project guidance remains visible.

M8: Selected and implemented local linear detrending as the first approved project version of inline `process_repeatability`. The algorithm estimates short-term inline NIR variability as the sample standard deviation of local-linear residuals, with explicit window and exclusion parameters, no raw full-run SD substitution, no reference-residual substitution, and no automatic statistical outlier removal.

M9: Completed a USP <1010> formula-alignment audit for paired off-line calculations. Paired accuracy was confirmed as `New - Old` with a two-sided `100 * (1 - 2 * alpha)%` CI inside `[-d, +d]`. Added paired precision options for known old variance and duplicate measurements, reclassified observed raw SD ratio as exploratory/supportive for heterogeneous paired samples, added a formula registry, and updated paired notebooks to make precision method selection explicit.

M10: Updated notebook report export to prevent wide pandas tables from being cropped in PDFs. PDF/HTML export now defaults to A4 landscape, removes the constrained notebook body width, forces print overflow visible for Jupyter output containers, wraps long dataframe cell content, and adds `display_report_dataframe` for compact report-facing dataframe previews.

M11: Refined notebook table export readability after wide-table PDF hardening. Header cells may still wrap, but data cells now keep values on one line with tabular numerals so numeric values are not split across PDF line breaks. One-row simulation and result-summary tables can be transposed to `parameter`/`value` layout with `transpose_if_one_row=True`.

M12: Added report-visible statistical theory and decision-rule sections to the paired off-line and inline notebooks. The sections provide concise paraphrased equations, hypotheses, generated input-value tables, and explicit statements that calculations and pass/fail decisions are performed by tested functions under `src/nir_cp/`, improving clean PDF reviewability without reproducing USP source text.

M13: Restored notebook theory equations to Markdown LaTeX notation and updated PDF export to wait for MathJax typesetting before headless printing. Also removed tablet side-position metadata from the Tablet Transmission NIR synthetic dataset and notebook/report text because this project version assumes one fixed tablet transmission measurement configuration through the same side/path.

M14: Added a notebook Markdown math regression guard so report theory sections fail tests if spaced dollar delimiters, plain-text formula names, or missing required LaTeX symbols are reintroduced. The PDF workflow documentation now states that display equations must use `$$` delimiters on separate lines and that PDF export depends on rendered MathJax output.

M15: Added Matplotlib mathtext SVG equation rendering for notebook report equations. Theory equations in the report notebooks are now generated by `nir_cp.report_equations.display_equation(...)` code cells whose inputs are hidden in clean PDF export, supplementing/replacing MathJax-dependent Markdown rendering for robust offline PDF reports.

M16: Added simulated-study notebooks for study-design exploration and teaching. The notebooks keep user-editable acceptance and simulation assumptions in one configuration cell, generate paired or inline synthetic study data from those assumptions, and then call the same tested analysis, decision, plotting, reporting, and export helpers used by the fixed-data report notebooks.
