# Regulatory Resource Handling

This repository may contain curated summaries, traceability matrices, tests, source code, notebooks, and synthetic examples. It must not contain protected regulatory source documents or real GMP/project data unless an explicit governance decision permits it.

## Private Resources

Store local copies of the following only in `resources/private/`:

- USP PDF files
- Comparability Protocol Word documents
- real product, batch, process, or GMP data
- private company source documents

`resources/private/` is ignored by Git. Do not move private source files into committed folders.

## Protected Source Text

Do not reproduce protected regulatory source text in committed files. Short curated summaries, project-specific interpretations, and traceability matrices may be committed when they do not copy protected source material.

## Traceability

All statistical logic must trace to documented decision rules. Use:

- `docs/STATISTICAL_DECISION_RULES.md`
- `docs/USP1010_TRACEABILITY_MATRIX.md`
- `docs/CP_METHOD_MODULES.md`
- `docs/DECISION_LOG.md`

When statistical logic changes, update tests and documentation in the same change.
