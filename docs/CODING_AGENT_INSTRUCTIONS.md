# Coding Agent Instructions

This is a notebook-first project, but safety-critical statistical decision logic must live in `src/nir_cp/` with tests.

Before modifying statistical code, future coding agents must read:

- `docs/STATISTICAL_DECISION_RULES.md`
- `docs/USP1010_TRACEABILITY_MATRIX.md`
- `docs/CP_METHOD_MODULES.md`
- `docs/DECISION_LOG.md`

Notebooks should call functions from `src/nir_cp/`. Do not bury statistical decision rules, pass/fail logic, or validated constants inside notebook cells.

Never change alpha defaults, confidence interval definitions, equivalence margins, precision ratio criteria, or pass/fail logic without updating tests and documentation in the same change.

Do not commit copyrighted or private regulatory source documents. Store local source documents in `resources/private/`, which is ignored by Git.
