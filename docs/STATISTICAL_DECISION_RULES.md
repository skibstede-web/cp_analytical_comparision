# Statistical Decision Rules

This document records implemented and intended statistical decision rules. Safety-critical decision logic is implemented in tested functions under `src/nir_cp/`.

Notebook reports include concise, paraphrased theory sections with equations and generated input-value tables. These sections explain the implemented rules but do not implement independent pass/fail logic.

## Paired Accuracy Equivalence

Implemented for paired off-line NIR method comparison when the same physical sample or tablet is measured by both the old and changed NIR method.

The paired difference is defined as:

$$
D_i = Y_{N,i} - Y_{O,i}
$$

with hypotheses:

$$
H_0: |\mu_D| \ge d
$$

$$
H_A: |\mu_D| < d
$$

The paired mean and variance are:

$$
\bar{D} = \frac{1}{n}\sum_{i=1}^{n}D_i
$$

$$
s_D^2 = \frac{\sum_{i=1}^{n}(D_i-\bar{D})^2}{n-1}
$$

The mean paired difference is summarized using a two-sided Student t confidence interval. For an alpha value of `0.05`, the paired accuracy equivalence procedure uses a two-sided `90%` confidence interval, calculated as `100 * (1 - 2 * alpha)%`.

$$
\bar{D} \pm t_{1-\alpha,n-1}\frac{s_D}{\sqrt{n}}
$$

The changed method passes paired accuracy equivalence when the full confidence interval for the mean paired difference lies inside the predefined equivalence margin:

$$
[-d, +d]
$$

The implemented function is `paired_accuracy_equivalence` in `src/nir_cp/statistics_usp1010.py`.

## Precision Noninferiority

Precision formula selection depends on study design. The formula registry in `docs/USP1010_FORMULA_REGISTRY.md` records the implemented options.

The general precision noninferiority hypotheses are:

$$
H_0: \frac{\sigma_N}{\sigma_O} \ge k
$$

$$
H_A: \frac{\sigma_N}{\sigma_O} < k
$$

### Independent or Exploratory Observed SD Ratio

The observed precision ratio is:

```text
ratio_observed = sample_sd_new / sample_sd_old
```

The one-sided upper confidence bound for `sigma_new / sigma_old` is calculated using the F distribution:

```text
upper_bound = sqrt((s_new^2 / s_old^2) / F_alpha(df_new, df_old))
```

where `s_old` and `s_new` are sample standard deviations with `ddof=1`, `df_old = n_old - 1`, and `df_new = n_new - 1`.

The changed method passes this observed SD-ratio noninferiority check when:

```text
upper_bound < k
```

where `k` is the predefined maximum acceptable precision ratio.

The implemented functions are `precision_ratio_upper_bound` and `precision_noninferiority` in `src/nir_cp/statistics_usp1010.py`.

This is an independent/total-observed SD ratio utility. It is not the preferred USP <1010> paired precision method for heterogeneous paired samples unless scientifically justified and CP-approved.

### Paired Precision With Known Old Variance

For a paired design with an approved old-method variance input, the paired difference is:

$$
D_i = Y_{N,i} - Y_{O,i}
$$

The sample variance of `D` is compared to the old-method variance using a lower chi-square quantile:

$$
U = \sqrt{\frac{(n-1)s_D^2}{\sigma_O^2\chi^2_{\alpha,n-1}} - 1}
$$

where `chi2_alpha_df` is the lower alpha quantile with `df = n - 1`. The check passes when:

$$
U < k
$$

The implemented function is `paired_precision_noninferiority_known_old_variance` in `src/nir_cp/statistics_usp1010.py`.

### Paired Precision With Duplicate Measurements

When independent duplicate measurements are available for each paired sample, duplicate-difference scaled values are:

$$
d_{O,i} = \frac{Y_{O,i,1}-Y_{O,i,2}}{\sqrt{2}}
$$

$$
d_{N,i} = \frac{Y_{N,i,1}-Y_{N,i,2}}{\sqrt{2}}
$$

The one-sided upper bound for `sigma_new / sigma_old` is:

```text
upper_bound = (sd_new_duplicate / sd_old_duplicate) * sqrt(1 / F_alpha(df_new, df_old))
```

The check passes when:

```text
upper_bound < k
```

The implemented function is `paired_precision_noninferiority_from_duplicate_measurements` in `src/nir_cp/statistics_usp1010.py`.

## Combined Paired Comparison Decision

For paired off-line NIR comparisons, `paired_comparison_decision` in `src/nir_cp/paired_comparison.py` runs both paired accuracy equivalence and selected precision noninferiority method.

The overall paired comparison passes only when both component criteria pass and the selected precision method is allowed as a primary criterion. The supported precision methods are:

- `known_old_variance`
- `duplicate_measurements`
- `observed_sd_ratio_exploratory`

The exploratory observed-SD method is supportive only unless explicitly justified and allowed.

## Probability-of-Success Simulation

Implemented for planning paired off-line NIR comparative studies before data are collected. The simulation engine is in `src/nir_cp/simulation.py`.

`simulate_paired_old_new_data` generates paired old-method and changed-method NIR values for a scenario with:

- old values centered at the specified method mean
- changed-method values centered at `mean + true_bias`
- separate old-method and changed-method standard deviations

`simulate_paired_comparison_success` repeatedly simulates paired datasets and calls the tested `paired_comparison_decision` function for each simulated study. It estimates:

- probability of passing paired accuracy equivalence
- probability of passing precision noninferiority
- probability of passing both criteria
- probability of failing each component criterion

`sample_size_grid` evaluates multiple planning scenarios across sample sizes, true bias values, and changed-method-to-old-method standard deviation ratios. It returns a pandas DataFrame intended for notebook reports and sample-size planning summaries.

Simulation output is planning evidence only. It does not replace the predefined pass/fail criteria used on observed comparative study data.

## Inline NIR Diversion-Control Performance Verification

Implemented as a first workflow for inline NIR diversion-control performance verification in `src/nir_cp/inline_diversion.py` and `notebooks/04_inline_diversion_performance_verification.ipynb`.

A classical paired old-vs-new USP <1010> comparison is not feasible for this inline use case because the old and changed inline methods cannot measure the exact same dynamic material stream under identical process conditions. The comparative pathway therefore uses historical old-method benchmarks, a prospective new-method run, extracted reference samples, precomputed process_repeatability values, diversion-zone assessment, and spectral diagnostics.

### Accuracy versus reference

For reference-aligned samples, error is defined as:

$$
e_i = Y_{NIR,i} - Y_{REF,i}
$$

The notebook-visible theory section defines:

$$
bias = \frac{1}{n}\sum_{i=1}^{n}e_i
$$

$$
MAE = \frac{1}{n}\sum_{i=1}^{n}|e_i|
$$

$$
RMSEP = \sqrt{\frac{1}{n}\sum_{i=1}^{n}e_i^2}
$$

The implemented accuracy summary reports the number of reference samples, mean bias, error standard deviation, mean absolute error, RMSEP, and minimum and maximum error.

The preliminary inline accuracy decision passes when:

```text
abs(mean_bias) <= d_inline
```

where `d_inline` is a preliminary or CP-approved inline bias criterion.

### Diversion-zone assessment

Each NIR prediction is classified relative to predefined lower and upper diversion limits. Without a guard band, the possible zones are:

- `below_lower_limit`
- `within_limits`
- `above_upper_limit`

The report-visible notation is:

$$
Y_{NIR,i} < L_{div}
$$

$$
L_{div} \le Y_{NIR,i} \le U_{div}
$$

$$
Y_{NIR,i} > U_{div}
$$

When a positive guard band is supplied, within-limit predictions near the lower or upper diversion limit can also be classified as:

- `within_guard_band_lower`
- `within_guard_band_upper`

### Process repeatability

The first implemented project algorithm for inline `process_repeatability` is local-linear-detrended residual variability. It is implemented in `src/nir_cp/process_repeatability.py`.

For a dynamic inline NIR prediction time series, the algorithm estimates short-term analytical/process-measurement variability after removing slow local process trends. For each eligible centre prediction point, it fits a local linear regression of NIR prediction versus time within a centred time window, then calculates:

$$
Y(t) = \beta_0 + \beta_1t + \epsilon
$$

$$
r_i = Y_i - \hat{Y}_i
$$

The `process_repeatability` value is:

$$
s_r = \sqrt{\frac{\sum_{i=1}^{n_r}(r_i-\bar{r})^2}{n_r-1}}
$$

This metric is not the raw full-run standard deviation and is not the standard deviation of reference-result residuals. It is based on NIR prediction residuals after local linear detrending.

Eligible rows are determined only by predefined validity rules:

- invalid spectra may be excluded when `exclude_invalid=True`
- diagnostic exceedances may be excluded only when `exclude_diagnostics=True` with predefined Q residual and/or Hotelling T2 limits
- statistical residual outlier removal is not applied automatically

All parameters must be explicit and reported, including time column, value column, window mode, `window_points` or `window_seconds`, `min_points`, validity exclusion settings, diagnostic exclusion settings, and unit.

The placeholder function `process_repeatability_placeholder` remains only for situations where precomputed company-approved process_repeatability values are used.

The preliminary repeatability decision compares the new run's process_repeatability, either calculated by the approved local-linear algorithm or supplied as an approved precomputed value, against the historical old-method mean calculated or supplied on the same basis:

```text
new_process_repeatability / historical_mean_process_repeatability <= k_inline
```

where `k_inline` is a preliminary or CP-approved ratio criterion.

### Overall preliminary decision

The inline preliminary decision passes only when both the accuracy and repeatability checks pass. This is a preliminary rule and must be replaced or confirmed by CP-approved criteria before GMP use.
