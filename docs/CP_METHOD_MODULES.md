# CP Method Modules

The workbench is intended to support three Comparability Protocol method modules.

## 1. Inline NIR Diversion Control

Inline NIR use case for diversion control during manufacturing. Planned analyses should compare legacy and proposed control behavior, including accuracy and precision checks where applicable.

Implemented notebook:

- `notebooks/04_inline_diversion_performance_verification.ipynb`

A classical paired old-vs-new USP <1010> comparison is not feasible for this inline dynamic-stream use case because the old and changed inline methods cannot measure the exact same material stream under identical process conditions.

The implemented workflow therefore follows this pathway:

- historical old-method performance benchmark
- prospective new-method process run
- extracted reference samples
- accuracy versus reference
- precomputed process_repeatability
- diversion decision-risk assessment
- spectral diagnostics and lifecycle monitoring

The current inline module supports local-linear-detrended `process_repeatability` as the first implemented precision metric option. This estimates short-term variability as the sample standard deviation of NIR prediction residuals after fitting local linear trends within explicit centred time windows. It is not raw full-run SD and is not reference-error SD.

The workflow also continues to support precomputed company-approved `process_repeatability` values from a run summary file for historical comparison. Historical and new-run comparisons should use the same approved algorithm or approved precomputed values consistently.

## 2. Off-line Granule Assay NIR

Off-line NIR method for granule assay. Planned analyses should support old-vs-new method comparison, simulation studies, and reportable statistical summaries.

Implemented notebook:

- `notebooks/02_granule_assay_paired_comparison.ipynb`

This notebook maps to paired granule assay studies where the same granule sample presentation is measured by both old and changed off-line NIR methods before reference analysis where feasible. It loads method-specific placeholder defaults from `config/method_defaults.yaml`, uses synthetic data from `examples/granule_assay_paired_example.csv`, and reports paired accuracy equivalence, precision noninferiority, supporting plots, and probability-of-success simulation.

The notebook explicitly calls out vial/sample presentation, refill, repacking, and related granule handling variability as study design factors.

Granule paired accuracy uses paired differences `New - Old`. Granule paired precision should use a CP-approved paired precision method such as known old-method variance or duplicate independent measurements. Raw SD ratio across heterogeneous paired samples is supportive/exploratory only unless scientifically justified and approved.

## 3. Off-line Tablet Transmission NIR

Off-line tablet transmission NIR method. Planned analyses should support paired procedure comparison, precision assessment, and notebook-based reporting for protocol evidence packages.

Implemented notebook:

- `notebooks/03_tablet_transmission_paired_comparison.ipynb`

This notebook maps to paired tablet transmission studies where the same intact tablet is measured by both old and changed transmission NIR methods, with reference analysis after NIR measurements where feasible. This project version assumes one fixed tablet transmission measurement configuration through the same side/path. It loads method-specific placeholder defaults from `config/method_defaults.yaml`, uses synthetic data from `examples/tablet_transmission_paired_example.csv`, and reports paired accuracy equivalence, precision noninferiority, supporting plots, and probability-of-success simulation.

The notebook explicitly calls out tablet weight, thickness, batch, strength, and the fixed transmission path as study design factors.

Tablet paired accuracy uses paired differences `New - Old`. Tablet paired precision should use a CP-approved paired precision method such as known old-method variance or duplicate independent measurements. Raw SD ratio across heterogeneous paired tablets is supportive/exploratory only unless scientifically justified and approved.

## Method Defaults

Method-specific defaults are stored in `config/method_defaults.yaml`. Current values are examples only and are not final validated acceptance criteria. They must be replaced with CP-approved method-specific criteria before GMP use.
