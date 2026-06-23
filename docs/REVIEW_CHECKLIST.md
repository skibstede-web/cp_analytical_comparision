# Review Checklist

Use this checklist before changing code, running analyses, sharing reports, or introducing non-synthetic data.

## Before Changing Statistical Code

- [ ] Read `docs/CODING_AGENT_INSTRUCTIONS.md`.
- [ ] Read `docs/STATISTICAL_DECISION_RULES.md`.
- [ ] Read `docs/USP1010_TRACEABILITY_MATRIX.md`.
- [ ] Read `docs/CP_METHOD_MODULES.md`.
- [ ] Read `docs/DECISION_LOG.md`.
- [ ] Confirm the proposed change does not silently alter alpha defaults, confidence interval definitions, equivalence margins, precision ratio criteria, or pass/fail logic.
- [ ] Update tests and documentation in the same change when decision logic changes.

## Before Running An Analysis

- [ ] Confirm the input data are the intended synthetic, development, or approved project dataset.
- [ ] Confirm method-specific criteria are approved for the intended use.
- [ ] Confirm notebooks call functions from `src/nir_cp/` rather than duplicating decision logic.
- [ ] Confirm any inline `process_repeatability` values are precomputed by an approved method.
- [ ] Record assumptions, data source, and configuration values in the notebook or report.

## Before Sharing A Report

- [ ] Confirm the report contains no protected regulatory source text beyond short permitted summaries.
- [ ] Confirm the report contains no real GMP data unless sharing is authorized.
- [ ] Confirm generated HTML/PDF files are stored under `reports/html/` or `reports/pdf/`.
- [ ] Confirm pass/fail statements match documented decision rules.
- [ ] Confirm preliminary criteria are clearly described as preliminary where applicable.

## Before Committing To GitHub

- [ ] Run `uv run pytest -q`.
- [ ] Check that generated reports, PDFs, DOCX files, caches, and private resources are not staged.
- [ ] Confirm `resources/private/` contains only local ignored files.
- [ ] Confirm examples remain synthetic and contain no real product, batch, process, or GMP identifiers.
- [ ] Confirm documentation changes are committed with behavior changes.

## Before Using With GMP/Project Data

- [ ] Confirm authorization to use the data in this local repository.
- [ ] Keep real data outside committed paths unless explicitly approved.
- [ ] Verify CP-approved statistical criteria before interpreting pass/fail output.
- [ ] Replace example method defaults with approved method-specific criteria.
- [ ] For inline diversion workflows, provide the approved company-specific `process_repeatability` algorithm or approved precomputed values.
- [ ] Have outputs reviewed by the responsible statistical, analytical, and regulatory reviewers.
