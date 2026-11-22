# Adaptive Market Risk & Volatility Intelligence System

## Research Decision Log --- Forecast Combination & Adaptive Evidence Weighting

**Status:** Methodology documented before implementation\
**Stage:** NIFTY baseline volatility modelling → forecast combination

## 1. Research question

The NIFTY out-of-sample experiments show that asymmetric volatility
models contain useful information relative to historical volatility,
EWMA, and symmetric GARCH-t. GJR-GARCH-t and EGARCH-t, however, are
statistically indistinguishable under the current HAC-adjusted
forecast-loss comparison.

The next question is:

> Can multiple statistically competitive forecasts be combined
> mathematically to produce a more robust volatility estimate?

The combination methods below are hypotheses to be tested, not
assumptions that they will improve performance.

## 2. Current evidence

OOS period: **2024-01-01 to 2026-09-22**\
Observations: **673**

  Model                             MAE      RMSE
  --------------------------- --------- ---------
  Historical 20D                0.4923%   0.6564%
  EWMA (λ=0.94)                 0.4924%   0.6419%
  GARCH-t                       0.4966%   0.6359%
  GJR-GARCH-t                   0.4626%   0.5818%
  EGARCH-t                      0.4628%   0.5796%
  GJR + EGARCH equal-weight     0.4623%   0.5793%

HAC-adjusted absolute-error comparison showed that GJR-GARCH-t has lower
forecast loss than Historical 20D, EWMA, and GARCH-t, while GJR vs
EGARCH is not statistically significant.

The equal-weight ensemble has a marginally lower MAE/RMSE than either
asymmetric component, but its HAC comparisons versus GJR and EGARCH are
not statistically significant.

## 3. Mathematical framework

For K candidate forecasts:

$$
\hat{\sigma}^{*}_t =
\sum_{i=1}^{K} w_{i,t}\hat{\sigma}_{i,t}
$$

subject to:

$$
w_{i,t}\geq0,
\qquad
\sum_i w_{i,t}=1
$$

The research problem is therefore the design and validation of the
weights.

## 4. Weighting strategies to test

### 4.1 Equal weighting

$$
w_i=\frac{1}{K}
$$

Purpose: simplest diversification benchmark.

### 4.2 Linear rank weighting

For rank i from strongest to weakest:

$$
w_i\propto K-i+1
$$

For five models this begins with the sequence:

$$
[5,4,3,2,1]
$$

followed by normalization.

### 4.3 Rank-reciprocal weighting

$$
w_i=
\frac{1/r_i}{\sum_j1/r_j}
$$

This emphasizes higher-ranked models while retaining positive weights
for other models.

### 4.4 Exponential/geometric rank weighting

$$
w_i=
\frac{\exp[-\lambda(r_i-1)]}
{\sum_j\exp[-\lambda(r_j-1)]}
$$

Small λ approaches equal weighting; larger λ concentrates weight toward
higher-ranked models.

This is the formal version of the proposed "expansion-series" idea.

### 4.5 Inverse-loss weighting

Using development-period loss L_i:

$$
w_i=
\frac{1/L_i}{\sum_j1/L_j}
$$

This uses the magnitude of forecast performance rather than only rank.

### 4.6 Softmax loss weighting

$$
w_i=
\frac{\exp(-\lambda L_i)}
{\sum_j\exp(-\lambda L_j)}
$$

This provides a controlled transition between diversification and
concentration.

### 4.7 Rolling performance weighting

Let L_i,t be the recent rolling loss:

$$
w_{i,t}=
\frac{\exp(-\lambda L_{i,t})}
{\sum_j\exp(-\lambda L_{j,t})}
$$

This allows the combination to adapt as model performance changes.

### 4.8 Regime-conditional weighting

Eventually:

$$
w_{i,t}=f(L_{i,t},Regime_t)
$$

Potential regimes include low volatility, normal, elevated volatility,
and stress/crisis. These must be empirically defined rather than
assumed.

## 5. Future information-weighting framework

After the statistical forecast-combination layer is validated,
additional information can be introduced:

**Statistical volatility:** Historical, EWMA, GARCH, GJR, EGARCH.

**Implied volatility:** India VIX, options IV, IV term structure, IV
skew.

**Derivatives positioning:** open interest, changes in OI, put/call
measures, futures basis and positioning.

**Global factors:** S&P 500, US VIX, USD/INR, US 10Y, Brent.

The principle is:

> Additional variables must demonstrate incremental information rather
> than being included simply because they are available.

A later evidence-score framework may take the form:

$$
E_{i,t}=
\alpha E^{forecast}_{i,t}
+\beta E^{risk}_{i,t}
+\gamma E^{regime}_{i,t}
+\delta E^{stability}_{i,t}
$$

followed by:

$$
w_{i,t}=
\frac{\exp(\lambda E_{i,t})}
{\sum_j\exp(\lambda E_{j,t})}
$$

This is a planned direction, not an implemented model.

## 6. Anti-overfitting rules

1.  Weighting rules must be specified before final OOS evaluation.
2.  Future OOS performance must never determine historical weights.
3.  λ and other tuning parameters must not be selected using the same
    observations used for final evaluation.
4.  Development, validation, and final OOS periods should be separated
    where practical.
5.  Walk-forward evaluation should eventually be preferred for adaptive
    weighting.
6.  Every combination must be compared against simple benchmarks.
7.  Complexity must earn its place through measurable OOS improvement.
8.  Statistical significance and economic relevance must be evaluated
    separately.
9.  A numerically lower error is not automatically a meaningful
    improvement.
10. If a complex method does not improve robustly, retain the simpler
    method.

## 7. Planned experimental sequence

``` text
Individual volatility forecasts
        ↓
Equal-weight combination
        ↓
Linear rank weighting
        ↓
Rank-reciprocal weighting
        ↓
Exponential rank weighting
        ↓
Inverse-loss weighting
        ↓
Softmax loss weighting
        ↓
Rolling adaptive weighting
        ↓
Regime-conditional weighting
        ↓
Add India VIX
        ↓
Test incremental information
        ↓
Add derivatives information
        ↓
Test incremental information
        ↓
Add global factors
        ↓
Regime/adaptive forecasting system
```

Each stage must be evaluated before proceeding.

## 8. Evaluation framework

Forecast accuracy:

-   MAE
-   RMSE
-   QLIKE after establishing a suitable realized-variance target

Statistical comparison:

-   HAC-adjusted forecast-loss comparisons
-   pairwise loss differentials
-   robustness to alternative HAC bandwidths

Robustness:

-   different evaluation windows
-   different volatility regimes
-   stress periods
-   alternative forecast horizons

Later risk evaluation:

-   VaR
-   Expected Shortfall
-   stress testing
-   economic value

## 9. Current target limitation

The current one-day target is:

$$
|\log(r_t)|
$$

This is a preliminary volatility proxy, not a direct observation of
latent volatility.

Before making stronger volatility-forecasting claims or relying heavily
on QLIKE, a more defensible realized-volatility target should be
constructed, potentially using future squared returns:

$$
RV_{t,t+h}
=
\sqrt{
\frac{1}{h}
\sum_{i=1}^{h}r_{t+i}^2
}
$$

Therefore, current combination results should be described as
preliminary OOS forecast evidence.

## 10. Current decision

**Completed:** NIFTY return analysis, volatility clustering analysis,
ARCH-LM, GARCH-t, GJR-GARCH-t, EGARCH-t, strict OOS comparison, MAE/RMSE
evaluation, DM-style comparison, HAC-adjusted comparison, equal-weight
GJR+EGARCH ensemble, and HAC-adjusted ensemble comparison.

**Decision:** Retain the GJR+EGARCH ensemble as a candidate, but do not
claim statistically significant improvement over either individual
asymmetric model.

**Next experiment:** Test predefined mathematical weighting schemes on
the current five-model forecast set, beginning with simple and
interpretable methods before moving toward adaptive weighting.

**Not yet implemented:** India VIX, derivatives information, global
factors, regime detection, adaptive ML, VaR/ES, and economic value
analysis.

## 11. Research philosophy

$$
\boxed{
Financial\ Theory
\rightarrow
Statistical\ Evidence
\rightarrow
Mathematical\ Combination
\rightarrow
OOS\ Validation
\rightarrow
Risk\ Decision
}
$$

Mathematical sophistication should be retained only when it improves
robustness, interpretability, or the quality of the financial decision.
