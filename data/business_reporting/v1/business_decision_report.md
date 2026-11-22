# Adaptive Market Risk Intelligence System
## Business Decision Report — Version 1

**Generated (UTC):** 2026-10-13T18:44:32+00:00

**Evaluation period:** 2026-01-01 to 2026-09-22  
**Evaluation observations:** 178  
**Source policy status:** FROZEN

---

## 1. Executive summary

This report consolidates the existing business evaluation, transaction-cost
analysis, and robustness analysis for the adaptive exposure strategy.

The central decision question is whether changing exposure according to
predefined risk regimes improved outcomes relative to a static exposure
baseline during the historical evaluation period.

The robustness analysis reports a positive adaptive-minus-static
compounded-return difference in each of the six scenarios evaluated.
However, the full-period compounded returns for both strategies were
negative. These results therefore support a preliminary finding of relative
downside management in this historical sample, not a claim of profitability,
predictive certainty, or live-trading readiness.

## 2. Evaluation design and governance

- The business decision dataset and policy are treated as existing inputs.
- The policy is not recalibrated by this report.
- The transaction-cost results are taken from the existing cost-analysis
  outputs; this script does not rerun their calculations.
- Robustness results are reported as produced by the existing robustness
  analysis.
- The evaluation period is historical and does not establish future results.

Policy status matches between the policy and robustness summary: `FROZEN`.

## 3. Business evaluation

The original business-evaluation summary is represented in the supporting
metrics file, `decision_metrics.csv`. It preserves the metric names and values
extracted from the source summary JSON.

The detailed daily evaluation data remains available in the original
`business_evaluation.csv`. No original evaluation output has been changed.

## 4. Transaction-cost sensitivity

The transaction-cost analysis source contains **1,068 rows** and the
following columns:

`Date`, `Strategy`, `Transaction_Cost_bps`, `Exposure`, `Log_Return`, `Gross_Return`, `Turnover`, `Transaction_Cost_Fraction`, `Net_Return`, `Net_Wealth`

The full detailed source table is reproduced as `transaction_cost_comparison.csv`.
Use its existing scenario and strategy fields to compare results across the
5, 10, and 20 basis-point assumptions. The scenarios represent simplified
cost assumptions; they do not establish actual execution costs.

## 5. Robustness results

The following comparison is sourced from the existing robustness summary.

| scenario | scenario_type | observations | static_compounded_return | adaptive_compounded_return | adaptive_minus_static_compounded_return | static_maximum_drawdown | adaptive_maximum_drawdown | static_annualized_volatility | adaptive_annualized_volatility | adaptive_mean_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Full_Evaluation | Chronological_Subperiod | 178 | -0.1071811145690148 | -0.06053796579141957 | 0.046643148777595234 | -0.15181809374299327 | -0.08472961205497154 | 0.14723286994950185 | 0.09084475893955962 | 0.756179775280899 |

### All evaluated scenarios

| scenario | scenario_type | observations | static_compounded_return | adaptive_compounded_return | adaptive_minus_static_compounded_return | static_maximum_drawdown | adaptive_maximum_drawdown | static_annualized_volatility | adaptive_annualized_volatility | adaptive_mean_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Full_Evaluation | Chronological_Subperiod | 178 | -0.1071811145690148 | -0.06053796579141957 | 0.046643148777595234 | -0.15181809374299327 | -0.08472961205497154 | 0.14723286994950185 | 0.09084475893955962 | 0.756179775280899 |
| First_Half | Chronological_Subperiod | 89 | -0.09514495616239682 | -0.05722250837849474 | 0.03792244778390208 | -0.15181809374299327 | -0.08472961205497154 | 0.18176678260180135 | 0.09453300515074134 | 0.6292134831460675 |
| Second_Half | Chronological_Subperiod | 89 | -0.01330175312453541 | -0.003516691310929354 | 0.009785061813606055 | -0.06683139865356214 | -0.06457502821172467 | 0.10223735496517777 | 0.08725766175102305 | 0.8831460674157303 |
| Frozen_Baseline | Hypothetical_Exposure_Mapping | 178 | -0.1071811145690148 | -0.06053796579141957 | 0.046643148777595234 | -0.15181809374299327 | -0.08472961205497154 | 0.14723286994950185 | 0.09084475893955962 | 0.756179775280899 |
| Mild_DeRisking | Hypothetical_Exposure_Mapping | 178 | -0.1071811145690148 | -0.07899154509470308 | 0.028189569474311726 | -0.15181809374299327 | -0.10909337946123643 | 0.14723286994950185 | 0.10961280514250622 | 0.8499999999999999 |
| Stronger_DeRisking | Hypothetical_Exposure_Mapping | 178 | -0.1071811145690148 | -0.05185915500894467 | 0.05532195956007013 | -0.15181809374299327 | -0.07105854770002817 | 0.14723286994950185 | 0.07795238240394048 | 0.6696629213483147 |

The chronological half-periods are descriptive subperiod checks, not
independent out-of-sample validation. The alternative exposure mappings are
hypothetical sensitivity scenarios; they do not demonstrate that any mapping
is optimal.

## 6. Business interpretation

The evidence is consistent with the adaptive strategy reducing market
exposure during selected higher-risk regimes and improving its historical
result relative to the static baseline under the evaluated assumptions.

That conclusion must be kept narrow:

1. Both strategies recorded negative compounded returns over the full
   evaluation period.
2. The result depends on the selected evaluation period, frozen thresholds,
   exposure mappings, zero-return cash assumption, and simplified target-exposure turnover proxy.
3. The transaction-cost scenarios are sensitivity tests, not verified
   brokerage or execution records.
4. Historical relative improvement is not proof of future performance.
5. This analysis alone does not justify capital allocation or live deployment.

## 7. Recommended next decision gates

Before treating the system as deployment-ready, the next stages should include:

- independent review of the return and turnover implementation;
- stress testing across additional market conditions and periods;
- realistic execution, slippage, taxes, and financing assumptions;
- monitoring of exposure changes and model/data failures;
- comparison against simple alternatives and predeclared decision criteria;
- a documented paper-trading or shadow-monitoring phase before any live use.

These are recommendations for further testing, not results already established
by the current analysis.

## 8. Reproducibility and supporting artifacts

- `decision_metrics.csv`: selected source-summary metrics with original keys.
- `transaction_cost_comparison.csv`: detailed transaction-cost source table.
- `robustness_comparison.csv`: detailed robustness source table.
- `report_manifest.json`: source hashes, output hashes, and build metadata.

All source files are expected to remain unchanged. The manifest records their
SHA-256 hashes for later independent verification.

## 9. Interpretation limits

This report summarizes existing analytical outputs; it does not constitute
investment advice, a guarantee of risk reduction, or evidence of realized
investor returns. No source result has been silently corrected or replaced.
