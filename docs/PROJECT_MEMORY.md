# Project Memory

## Purpose

Build a statistical workbench for NIR comparative studies supporting an EMA Comparability Protocol.

## Current Project Decisions

- Use UV for environment and dependency management.
- Use Python 3.12 only through `requires-python = ">=3.12,<3.13"`.
- Keep the project notebook-first for analysis and reporting.
- Keep a small tested helper package in `src/nir_cp/` for statistical decisions, simulation, plotting, reporting text, method config, inline diversion helpers, and notebook export.
- Keep notebooks as report surfaces that call tested helper functions rather than embedding pass/fail logic.
- Export final reports through styled HTML and optional headless Chrome/Edge/Chromium PDF printing.
- Use synthetic example data only in committed examples.

## Implemented Workflows

- General paired off-line old-vs-new NIR comparison.
- Off-line Granule Assay NIR paired comparison.
- Off-line Tablet Transmission NIR paired comparison.
- Inline NIR diversion-control performance verification.

## Statistical Scope

- Paired off-line workflows implement paired accuracy equivalence and precision noninferiority.
- Probability-of-success simulation is available for paired off-line study planning.
- Inline diversion workflow uses historical benchmarks, prospective new-run reference samples, diversion zones, spectral diagnostics, and precomputed `process_repeatability`.
- The inline company-specific `process_repeatability` algorithm is not implemented; approved values must be supplied as precomputed input until the approved algorithm is provided.

## Source Document And Data Handling

Protected regulatory source documents must not be committed. Local copies belong in `resources/private/`.

Real GMP/project data must not be committed. The repository examples are synthetic only.
