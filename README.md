# nir-cp-comparability

Notebook-first statistical workbench for NIR comparative studies supporting an EMA Comparability Protocol.

The project supports USP <1010>-aligned off-line procedure comparison, NIR old-vs-new method simulations, inline diversion-control performance verification, notebook reports, and PDF export. Safety-critical statistical functions live in `src/nir_cp/`; notebooks in `notebooks/` call those tested functions rather than embedding decision logic in notebook cells.

## Setup

- Python `>=3.12,<3.13`
- UV for dependency management

```powershell
uv sync
```

## Run Tests

```powershell
uv run pytest -q
```

## Execute Notebooks

Run a notebook from the repository root with nbconvert:

```powershell
uv run jupyter nbconvert --to notebook --execute notebooks/01_general_paired_offline_nir_comparison.ipynb --output executed_01_general_paired_offline_nir_comparison.ipynb --output-dir reports/html
```

Generated notebook outputs belong in `reports/html/` and are ignored by Git.

## Export PDF Reports

Notebook PDF export is implemented through styled HTML and a headless Chrome, Edge, or Chromium browser:

```python
from nir_cp.notebook_export import export_notebook_pdf

export_notebook_pdf(
    "notebooks/01_general_paired_offline_nir_comparison.ipynb",
    "reports/pdf/01_general_paired_offline_nir_comparison.pdf",
)
```

Generated PDFs belong in `reports/pdf/` and are ignored by Git.

## Available Notebooks

- `notebooks/01_general_paired_offline_nir_comparison.ipynb`: general paired off-line old-vs-new NIR comparison.
- `notebooks/02_granule_assay_paired_comparison.ipynb`: paired Off-line Granule Assay NIR comparison.
- `notebooks/03_tablet_transmission_paired_comparison.ipynb`: paired Off-line Tablet Transmission NIR comparison.
- `notebooks/04_inline_diversion_performance_verification.ipynb`: inline NIR diversion-control performance verification using historical benchmarks, a prospective new run, reference samples, precomputed process_repeatability, diversion zones, and spectral diagnostics.

## Repository Layout

- `src/nir_cp/`: tested helper code and statistical decision functions
- `notebooks/`: notebook-first analyses and reports
- `docs/`: project memory, decision rules, traceability, and workflow notes
- `resources/private/`: local regulatory or private source documents, ignored by Git
- `reports/html/` and `reports/pdf/`: generated report outputs, ignored by Git
- `tests/`: regression and import tests

## Data And Source Document Policy

The repository contains synthetic example data only. Files under `examples/` are illustrative and must not be treated as product, batch, process, or GMP data.

Do not commit protected regulatory documents, real GMP data, batch records, product data, or private company source documents. Store local copies only in `resources/private/`, which is ignored by Git. Curated markdown summaries, decision logs, and traceability matrices may be committed when they do not reproduce protected source material.

Before using project or GMP data, review:

- `docs/REVIEW_CHECKLIST.md`
- `docs/REGULATORY_RESOURCE_HANDLING.md`
- `docs/STATISTICAL_DECISION_RULES.md`
