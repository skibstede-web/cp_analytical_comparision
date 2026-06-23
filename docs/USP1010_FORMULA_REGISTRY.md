# USP <1010> Formula Registry

Curated project formula registry. This file summarizes formulas used by project code and does not reproduce protected USP source text. Notebook theory sections use concise paraphrased equations in project notation so exported PDF reports are understandable without copying USP source paragraphs.

| Formula concept | Project summary | Function(s) | Design scenario | Notes |
| --- | --- | --- | --- | --- |
| Mean and SD | Sample mean and sample SD with `ddof=1`. | `mean_ci_t` | General summaries | Used as ingredients for confidence intervals and variance comparisons. |
| Confidence interval for mean | Student t two-sided confidence interval for a one-sample mean. | `mean_ci_t` | Mean or paired-difference summaries | Confidence level is explicit. |
| Accuracy equivalence, paired TOST logic | Difference is `D = New - Old`; use two-sided `100 * (1 - 2 * alpha)%` CI for mean `D`; pass if full CI is inside `[-d, +d]`. | `paired_accuracy_equivalence` | Paired old-vs-new samples/tablets | Implemented for off-line paired NIR comparisons. |
| Independent precision ratio upper bound | Upper bound for `sigma_new / sigma_old` using observed SD ratio and F distribution. | `precision_ratio_upper_bound`; `precision_noninferiority` | Independent homogeneous-material precision studies or exploratory observed SD comparison | Not the preferred paired precision method for heterogeneous paired samples unless justified. |
| Paired precision using known old variance | Use variance of paired differences and known old-method variance with lower chi-square quantile to bound additional new-method variance component. | `paired_precision_noninferiority_known_old_variance` | Paired design with approved old variance input | Raises an error if the square-root expression is negative. |
| Paired precision using duplicate measurements | Use duplicate-difference scaled values for old and new methods; compare duplicate SD ratio with F-distribution upper bound. | `paired_precision_noninferiority_from_duplicate_measurements` | Paired samples with independent duplicate measurements by both methods | Requires matched duplicate arrays and nonzero old duplicate SD. |
| Sample-size/power simulation concept | Repeatedly simulate studies and evaluate predefined decision rules to estimate probability of success. | `simulate_paired_comparison_success`; `sample_size_grid` | Planning support | Simulation is planning evidence only and does not replace observed-data decision rules. |
| Inline process_repeatability | Project-specific local-linear-detrended residual SD for dynamic inline NIR predictions. | `calculate_process_repeatability` | Non-paired inline diversion-control verification | Precision surrogate for inline lifecycle verification; not a USP <1010> paired formula. |

Notebook reports contain generated "Values used in this notebook" tables. Those tables display runtime inputs for review, while pass/fail calculations remain in tested functions under `src/nir_cp/`.
