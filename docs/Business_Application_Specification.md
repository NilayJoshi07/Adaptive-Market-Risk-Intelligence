# Adaptive Market Risk Intelligence System

## Business Application Specification

### 1. Purpose

The Adaptive Market Risk Intelligence System translates validated NIFTY 50 volatility forecasts into a practical market-risk and portfolio-exposure decision framework.

The system is designed as a **decision-support and risk-management system**, not as an autonomous trading system or a guaranteed return-generation strategy.

Its purpose is to help an investment-management organization answer:

> **Given the estimated market-volatility environment, how should portfolio exposure to NIFTY-linked market risk be managed?**

---

## 2. Business Context

### Target Organization

The intended business context is a hypothetical:

**Asset Management / Investment Management organization**

with portfolio exposure to the NIFTY 50.

### Business User

Primary users include:

* Portfolio managers
* Investment analysts
* Market-risk analysts
* Risk managers
* Investment-management decision makers

### Business Problem

Market risk changes over time. A portfolio maintained at constant exposure may remain heavily exposed during periods of elevated or extreme volatility.

The system therefore attempts to provide an evidence-based mechanism for:

* identifying changing volatility conditions;
* classifying market-risk regimes;
* translating those regimes into predefined exposure levels; and
* evaluating whether such exposure management can reduce downside risk.

---

## 3. Research Foundation

The business application consumes the outputs of the validated empirical research layer.

The research layer established that:

1. NIFTY 50 volatility can be forecast using time-series models.
2. Adaptive calibration improves forecasting performance.
3. India VIX provides incremental information for NIFTY 50 volatility forecasting.
4. These findings persist under strict out-of-sample evaluation.
5. Predictive-loss improvements for the principal VIX-enhanced models are statistically significant.
6. The forecasting system has been designed to respect the available information set and avoid look-ahead bias.

The business layer does **not** independently re-estimate or modify the validated forecasting models.

---

## 4. Frozen Forecasting Input

The primary forecasting signal selected for the business application is:

> **EGARCH_t_VIX**

It was selected using the business-development period rather than the held-out 2026 evaluation period.

The business application therefore consumes the frozen Research Output v1 rather than recalculating the research models.

This separation preserves reproducibility and prevents the business layer from contaminating the research evaluation.

---

## 5. Evaluation Architecture

The business application uses:

### Development period

**1 January 2024 – 31 December 2025**

Purpose:

* model selection;
* business-policy calibration;
* development of the exposure framework.

### Held-out evaluation period

**1 January 2026 – 22 September 2026**

Observations:

**178 trading days**

The held-out period is not used to select the primary forecasting model or tune the exposure policy.

---

## 6. Risk Intelligence Layer

The forecasted volatility is converted into a discrete risk regime.

The system uses five regimes:

| Risk Regime | Interpretation                      |
| ----------- | ----------------------------------- |
| Low         | Relatively low estimated volatility |
| Normal      | Normal estimated volatility         |
| Elevated    | Increasing risk conditions          |
| High        | Material risk elevation             |
| Extreme     | Severe estimated risk conditions    |

The regimes are intended to make quantitative forecasts interpretable for business decision makers.

They do not represent predictions of market direction.

---

## 7. Exposure Decision Policy

The current business policy maps risk regimes to target portfolio exposure:

| Risk Regime | Target Exposure |
| ----------- | --------------: |
| Low         |            100% |
| Normal      |            100% |
| Elevated    |             80% |
| High        |             60% |
| Extreme     |             40% |

These exposure levels are **policy assumptions used for the business simulation**.

They should not be described as universally optimal portfolio weights.

The purpose of the simulation is to test whether a transparent volatility-aware exposure policy can generate measurable downside-risk benefits.

---

## 8. Benchmark

The adaptive framework is compared against a static benchmark:

> **100% NIFTY exposure throughout the evaluation period.**

The benchmark represents a constant-exposure portfolio and provides a transparent counterfactual against which the adaptive framework can be evaluated.

---

## 9. Portfolio Simulation

For each evaluation date:

```text
Forecasted Volatility
        ↓
Risk Regime
        ↓
Target Exposure
        ↓
NIFTY Return
        ↓
Portfolio Return
        ↓
Transaction Cost
        ↓
Net Portfolio Return
        ↓
Compounded Wealth
```

The adaptive portfolio return is therefore determined by the exposure assigned to the prevailing risk regime.

Portfolio wealth is calculated using compounded returns:

$$
W_t = \prod_{i=1}^{t}(1+r_i)
$$

The final compounded return is:

$$
R_T = W_T-1
$$

Arithmetic sums of daily returns may be retained as supplementary diagnostics but are not treated as compounded portfolio returns.

---

## 10. Transaction-Cost Framework

Exposure changes generate illustrative transaction costs.

The current central sensitivity assumption is:

> **10 basis points (0.10%) per unit of absolute exposure change.**

Additional sensitivity scenarios are evaluated at:

* 5 bps
* 10 bps
* 20 bps

The transaction-cost analysis is a sensitivity framework rather than an estimate of actual institutional execution costs.

---

## 11. Business Impact KPIs

The primary business-impact metrics are:

### Performance

* Compounded total return
* Annualized return

### Risk

* Annualized volatility
* Maximum drawdown
* Negative-return downside variability

### Risk-adjusted performance

* Sharpe ratio
* Sortino ratio

### Exposure management

* Average exposure
* Exposure reduction
* High/Extreme regime frequency
* Exposure during High/Extreme regimes

### Implementation

* Exposure changes
* Absolute exposure turnover
* Illustrative transaction costs

---

## 12. Primary Business Questions

The system should answer four core questions:

### Question 1

**Does adaptive exposure management reduce the magnitude of portfolio losses?**

### Question 2

**Does adaptive exposure management reduce volatility and maximum drawdown?**

### Question 3

**Do the observed benefits remain after illustrative transaction costs?**

### Question 4

**Are the benefits concentrated in elevated-risk regimes?**

These questions define the scope of the business-impact analysis.

---

## 13. Current Business Evidence

The held-out 2026 evaluation produced:

| KPI                   |  Static | Adaptive |
| --------------------- | ------: | -------: |
| Compounded return     | −10.72% |   −6.65% |
| Annualized volatility |  14.72% |    9.11% |
| Maximum drawdown      | −15.18% |   −8.64% |
| Sharpe                |   −1.01 |    −1.02 |
| Sortino               |   −0.98 |    −1.02 |

Additional exposure results:

* Average adaptive exposure: **75.62%**
* Average exposure reduction: **24.38%**
* High + Extreme observations: **61 / 178**
* Average High + Extreme exposure: **43.61%**
* Estimated transaction cost under 10-bps assumption: **0.64%**

After transaction costs, the adaptive portfolio still produced a smaller compounded loss than the static benchmark.

However, the Sharpe and Sortino differences remained slightly negative.

---

## 14. Business Interpretation

The strongest supported interpretation is:

> **The system demonstrates potential downside-risk and exposure-management value rather than established return-enhancement value.**

During the evaluated period, adaptive exposure management:

* reduced portfolio exposure during higher-risk regimes;
* reduced annualized volatility;
* reduced maximum drawdown;
* produced a smaller compounded loss than static exposure; and
* retained the terminal-loss advantage after the illustrative transaction-cost assumption.

However:

* Sharpe did not improve;
* Sortino did not improve;
* profitability was not established;
* future performance is not guaranteed.

Therefore, the system should be positioned as a **risk-management and decision-support framework**.

---

## 15. What the System Does Not Claim

The system does not currently establish that:

* the strategy is universally profitable;
* adaptive exposure always outperforms static exposure;
* the exposure policy is optimal;
* the system improves Sharpe or Sortino in every market environment;
* the system minimizes portfolio risk under all conditions;
* the model generates trading signals;
* the model provides investment advice;
* the model guarantees future performance.

These claims require additional evidence and should not be included in project marketing or reporting.

---

## 16. Governance Principle

The system is designed as:

> **Decision support, not autonomous decision making.**

The final portfolio decision remains with the investment or risk-management professional.

The system provides:

* forecast information;
* risk classification;
* exposure guidance;
* historical business-impact evidence.

It does not independently execute trades.

---

## 17. Future Analytical Extensions

Future extensions may include:

### SQL

A structured analytical data layer for:

* market data;
* forecasts;
* risk regimes;
* exposure decisions;
* portfolio performance;
* business KPIs.

### Machine Learning

Potential future research question:

> Can machine-learning models improve the probability assessment of transitions into High or Extreme volatility regimes?

ML should be introduced only if it provides incremental decision value.

### Power BI

Management-facing reporting layer for:

* current risk state;
* exposure guidance;
* historical regime analysis;
* portfolio-risk KPIs;
* business-impact monitoring.

### Streamlit

Interactive decision-support application integrating:

* forecast information;
* risk regime;
* exposure recommendation;
* historical business impact.

These extensions must consume the frozen research and business definitions rather than silently changing them.

---

## 18. System Architecture

The complete intended architecture is:

```text
                    MARKET DATA
                        │
              ┌─────────┴─────────┐
              │                   │
           NIFTY 50           INDIA VIX
              │                   │
              └─────────┬─────────┘
                        ↓
              VOLATILITY ENGINE
                        │
                        ↓
                EGARCH + VIX
                        │
                        ↓
              RISK INTELLIGENCE
                        │
                        ↓
                  RISK REGIME
                        │
                        ↓
              EXPOSURE DECISION
                        │
                        ↓
              PORTFOLIO SIMULATION
                        │
                        ↓
               BUSINESS IMPACT
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
         SQL            ML         Analytics
          │             │             │
          └─────────────┼─────────────┘
                        ↓
                    POWER BI
                        │
                        ↓
                   STREAMLIT
```

The research engine remains the authoritative analytical foundation.

---

## 19. Final Business Objective

The ultimate objective of the system is not simply to forecast volatility.

It is to establish a reproducible chain from:

> **Market information → volatility forecast → risk intelligence → exposure decision → measurable financial impact.**

This creates a bridge between quantitative finance research and practical business decision support.

---

## 20. Final Positioning

The Adaptive Market Risk Intelligence System is therefore positioned as:

> **A quantitative market-risk decision-support system that combines NIFTY 50 volatility modelling, India VIX information, adaptive forecasting, risk-regime classification, and volatility-aware exposure management to evaluate potential downside-risk benefits for an investment-management portfolio.**

The research layer establishes forecasting evidence.

The business layer evaluates whether that forecasting information can translate into measurable risk-management value.

Future SQL, ML, Power BI, and Streamlit components must preserve this separation and build on these frozen definitions.
