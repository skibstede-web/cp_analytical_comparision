# USP <1010> Traceability Matrix

This matrix maps high-level USP <1010>-aligned procedure comparison concepts to project implementation artifacts. It is a curated traceability summary and does not reproduce source standard text.

| USP <1010> concept | Project implementation | File/function/notebook | Status | Notes |
| --- | --- | --- | --- | --- |
| Study objective | Compare old and changed NIR procedures or verify inline diversion-control performance against predefined criteria. | `docs/CP_METHOD_MODULES.md`; notebooks in `notebooks/` | Implemented initial workflows | Objectives must be refined for each CP method module before GMP use. |
| Study design | Paired off-line design when the same physical sample/tablet can be measured by both methods; historical/prospective non-paired pathway for inline diversion. | `notebooks/01_general_paired_offline_nir_comparison.ipynb`; `notebooks/02_granule_assay_paired_comparison.ipynb`; `notebooks/03_tablet_transmission_paired_comparison.ipynb`; `notebooks/04_inline_diversion_performance_verification.ipynb` | Implemented examples | Example datasets are synthetic only. |
| Accuracy equivalence | Paired mean difference confidence interval must lie within `[-d, +d]` for off-line paired workflows. | `paired_accuracy_equivalence` in `src/nir_cp/statistics_usp1010.py` | Implemented and tested | Margins in examples are placeholders unless CP-approved. |
| Precision noninferiority | Formula depends on design: independent SD ratio, paired known old variance, or paired duplicate measurements. | `precision_ratio_upper_bound`; `paired_precision_noninferiority_known_old_variance`; `paired_precision_noninferiority_from_duplicate_measurements` in `src/nir_cp/statistics_usp1010.py` | Implemented and tested | Observed SD ratio across heterogeneous paired samples is exploratory/supportive only unless justified. |
| Paired design | Uses `new - old` differences for the same sample/tablet in paired off-line workflows. | `paired_comparison_decision` in `src/nir_cp/paired_comparison.py` | Implemented and tested | Applies to Granule Assay NIR and Tablet Transmission NIR when true pairing is feasible. |
| Uncertainty/confidence intervals | Student t interval for mean paired difference; F-distribution upper bound for independent/duplicate precision ratio; chi-square bound for paired known-old-variance precision. | `mean_ci_t`; `paired_accuracy_equivalence`; precision functions in `src/nir_cp/statistics_usp1010.py` | Implemented and tested | Defaults documented in `docs/STATISTICAL_DECISION_RULES.md`. |
| Randomization/representativeness | Not automated; notebooks expose batch/sample metadata and example planning simulations. | Example CSVs; notebooks; `simulate_paired_comparison_success` in `src/nir_cp/simulation.py` | Partially implemented | Study teams must define sampling strategy, representativeness, and run order in the protocol. |
| Avoiding post-hoc decision rules | Decision criteria are parameters and documented rules, with tests guarding pass/fail logic. | `docs/STATISTICAL_DECISION_RULES.md`; `config/method_defaults.yaml`; tests in `tests/` | Implemented guardrails | Example defaults are placeholders and must be replaced before GMP use. |
| Inline non-paired limitation | Inline diversion-control cannot use exact paired old/new dynamic-stream measurements; workflow uses historical old benchmark and prospective new run. | `src/nir_cp/inline_diversion.py`; `src/nir_cp/process_repeatability.py`; `notebooks/04_inline_diversion_performance_verification.ipynb` | Implemented preliminary workflow | Local-linear process_repeatability is a project-specific non-paired precision surrogate, not a USP <1010> paired formula. |

## Notebook Theory Sections

The report notebooks include visible `Statistical theory and decision rules` sections for clean PDF exports with code hidden. These sections are concise paraphrases in project notation and do not reproduce source-standard text.

| Notebook theory content | Implemented function(s) | Notebook(s) | Notes |
| --- | --- | --- | --- |
| Paired study design and paired difference `D_i = Y_N - Y_O` | `paired_comparison_decision`; `paired_accuracy_equivalence` | `01_general_paired_offline_nir_comparison.ipynb`; `02_granule_assay_paired_comparison.ipynb`; `03_tablet_transmission_paired_comparison.ipynb` | Theory text states that pass/fail logic is in tested `src/nir_cp/` functions. |
| Paired accuracy equivalence CI and `[-d, +d]` decision rule | `paired_accuracy_equivalence`; `mean_ci_t` | Paired off-line notebooks | Matches tested TOST-style CI implementation. |
| Precision noninferiority method qualification | `paired_comparison_decision`; precision functions in `statistics_usp1010.py` | Paired off-line notebooks | Observed SD-ratio examples are visibly marked supportive/exploratory unless justified in the CP. |
| Generated values-used tables | `display_report_dataframe` | All report notebooks | Tables display runtime notebook inputs and do not duplicate pass/fail logic. |
| Inline accuracy versus reference metrics | `calculate_reference_errors`; `summarize_accuracy_vs_reference` | `04_inline_diversion_performance_verification.ipynb` | Metrics summarize agreement versus reference and are not a paired old/new USP <1010> comparison. |
| Inline diversion-zone equations | `classify_diversion_zone`; `summarize_diversion_decisions` | `04_inline_diversion_performance_verification.ipynb` | Guard-band interpretation is documented in the theory section. |
| Local-linear process_repeatability equations | `calculate_process_repeatability`; `process_repeatability_summary_frame` | `04_inline_diversion_performance_verification.ipynb` | Theory states this is not raw full-run SD and not reference-error SD. |
