# Frozen Baseline — Adaptive Market Risk Intelligence System

## Business Impact Baseline

**Notebook:** `Notebooks/02_business_impact.ipynb`
**Frozen Version:** v1.0
**Evaluation Period:** 2026-01-01 to 2026-09-22
**Evaluation Observations:** 178
**Primary Forecast Model:** EGARCH_t_VIX
**Transaction Cost Scenario:** 10 bps

## Research Input

The business-impact layer consumes the frozen Research Output v1 dataset and does not recalculate the underlying research models.

## Frozen Business Results

* Static compounded return: -10.7181%
* Adaptive net compounded return: -6.6549%
* Compounded return advantage vs static: +4.0632 percentage points
* Annualized volatility reduction: 38.12%
* Maximum drawdown reduction: 43.10%
* Average adaptive exposure: 75.62%
* Average exposure reduction: 24.38%
* High + Extreme observations: 61 of 178
* Average High + Extreme exposure: 43.61%
* Total illustrative transaction cost: 0.64%
* Sharpe difference: -0.0082
* Sortino difference: -0.0413
* Negative-return downside variability reduction: 40.16%

## Interpretation

The adaptive framework provides evidence of downside-risk and exposure-control benefits during the held-out evaluation period. The results do not establish superior risk-adjusted returns, guaranteed profitability, or universal outperformance.

## Versioning Rule

The frozen v1.0 baseline must not be silently overwritten.

Any methodological, data, policy, or calculation change that materially affects these results must create a new version rather than modifying the frozen baseline.

Examples:

* Research Output v2
* Business Impact v1.1
* Business Impact v2.0

Future SQL, ML, Power BI, and Streamlit components should consume the frozen baseline unless explicitly designated as experimental.
