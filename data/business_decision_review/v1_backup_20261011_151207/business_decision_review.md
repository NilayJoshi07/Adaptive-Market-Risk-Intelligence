# Business Decision Review
## Adaptive Market Risk Intelligence System — Version 1

**Generated (UTC):** 2026-10-09T18:41:15+00:00

**Evaluation period:** 2026-01-01 to 2026-09-22  
**Evaluation observations:** 178  
**Authoritative policy status:** FROZEN

---

## 1. Decision summary

**Current recommendation: continue validation; do not treat this evidence alone as deployment approval.**

The existing robustness summary reports full-period compounded returns of
-10.72% for the static baseline and -6.19% for the
adaptive strategy. The reported adaptive-minus-static difference is
4.52%.

These are historical model results under the project's existing simplified
return assumptions. Both strategies had negative compounded returns in the
full evaluation period. The positive relative difference therefore does not
establish absolute profitability, future risk reduction, or suitability for
live deployment.

## 2. Evidence reviewed

This review draws from the existing business evaluation, frozen decision
policy, transaction-cost analysis, robustness analysis, and validated
business decision report.

- Business evaluation observations: 178
- Decision dataset rows: 673
- Transaction-cost analysis rows: 1,068
- Robustness detail rows: 12
- Robustness scenarios in summary: 6

The detailed source-derived facts are preserved in `evidence_snapshot.csv`.
This review does not rerun or silently replace the source calculations.

## 3. Robustness evidence

| scenario | scenario_type | observations | static_compounded_return | adaptive_compounded_return | adaptive_minus_static_compounded_return | static_maximum_drawdown | adaptive_maximum_drawdown | static_annualized_volatility | adaptive_annualized_volatility | adaptive_mean_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Full_Evaluation | Chronological_Subperiod | 178 | -0.1071811145690148 | -0.06193128373990375 | 0.04524983082911105 | -0.15181809374299327 | -0.08547169126965692 | 0.14723286994950185 | 0.09086026455194345 | 0.756179775280899 |
| First_Half | Chronological_Subperiod | 89 | -0.09514495616239682 | -0.058424183400352714 | 0.03672077276204411 | -0.15181809374299327 | -0.08547169126965692 | 0.18176678260180135 | 0.09454264001240659 | 0.6292134831460675 |
| Second_Half | Chronological_Subperiod | 89 | -0.01330175312453541 | -0.0037247136956184423 | 0.009577039428916967 | -0.06683139865356214 | -0.06458586137982403 | 0.10223735496517777 | 0.08726875316095946 | 0.8831460674157303 |
| Frozen_Baseline | Hypothetical_Exposure_Mapping | 178 | -0.1071811145690148 | -0.06193128373990375 | 0.04524983082911105 | -0.15181809374299327 | -0.08547169126965692 | 0.14723286994950185 | 0.09086026455194345 | 0.756179775280899 |
| Mild_DeRisking | Hypothetical_Exposure_Mapping | 178 | -0.1071811145690148 | -0.0802116349138744 | 0.026969479655140405 | -0.15181809374299327 | -0.10975088564187208 | 0.14723286994950185 | 0.10963327065341712 | 0.8499999999999999 |
| Stronger_DeRisking | Hypothetical_Exposure_Mapping | 178 | -0.1071811145690148 | -0.05328384417691967 | 0.05389727039209513 | -0.15181809374299327 | -0.07179197443630392 | 0.14723286994950185 | 0.07795763649469281 | 0.6696629213483147 |

Chronological subperiods are descriptive checks, not independent validation.
Alternative exposure mappings are hypothetical sensitivity analyses and do
not establish an optimal policy. The results depend on the selected period,
frozen thresholds, exposure mapping, and simplified return model.

## 4. Governance and metadata issue

The authoritative `business_policy.json` reports `FROZEN`, while the robustness summary reports `NOT_SPECIFIED`. This discrepancy remains open; neither source was altered.

The discrepancy must be traced and documented. Any authorized correction
should be emitted as a new versioned artifact with its own hashes and
independent validation. Do not overwrite frozen source outputs merely to
remove a warning.

## 5. Priority actions

The detailed, editable action register is in `action_register.csv`.

1. Resolve or formally document the policy metadata inconsistency.
2. Independently reproduce the return, exposure, turnover, and drawdown
   calculations.
3. Extend cost assumptions and document exclusions.
4. Define untouched out-of-sample tests before inspecting their results.
5. Compare against additional predeclared alternatives using consistent
   dates and assumptions.
6. Define operational failure handling, monitoring, and escalation.
7. Consider paper-trading or shadow monitoring only after prior analytical
   and operational gates are satisfied.

All action statuses in the register are proposed project-management states,
not claims that work has already been completed.

## 6. Decision gates

The detailed gate register is in `decision_gates.csv`. Each gate currently
remains unpassed or blocked pending earlier gates. The exit criteria are
proposed criteria for review and approval, not historical results.

No deployment decision should be inferred from this report. A future
decision should be made separately after the required evidence is produced,
reviewed, and documented.

## 7. Interpretation limits

- The analysis is historical and does not guarantee future outcomes.
- Both strategies had negative compounded returns over the full evaluation
  period.
- Transaction-cost scenarios are not verified execution records.
- The alternative exposure mappings do not prove policy optimality.
- Chronological halves are not independent samples.
- This review does not establish realized investor returns or live-trading
  readiness.

## 8. Reproducibility

`review_manifest.json` records the input hashes and generated-output hashes.
The source files are read-only inputs to this process. The report, action
register, decision gates, and evidence snapshot are new versioned artifacts.
