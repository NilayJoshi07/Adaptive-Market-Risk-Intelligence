
from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Decision Support & Scenario Lab | AMRIS",
    page_icon="⚖️",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EVALUATION_DIR = (
    PROJECT_ROOT / "data" / "business_evaluation" / "v1"
)
DECISION_DIR = (
    PROJECT_ROOT / "data" / "business_decision" / "v1"
)
REPORTING_DIR = (
    PROJECT_ROOT / "data" / "business_reporting" / "v1"
)

EVALUATION_FILE = EVALUATION_DIR / "business_evaluation.csv"
SUMMARY_FILE = EVALUATION_DIR / "business_evaluation_summary.json"
POLICY_FILE = DECISION_DIR / "business_policy.json"
TRANSACTION_COST_FILE = (
    EVALUATION_DIR / "cost_analysis" / "transaction_cost_analysis.csv"
)
ROBUSTNESS_FILE = REPORTING_DIR / "robustness_comparison.csv"


# ============================================================
# HELPERS
# ============================================================

def load_csv(path: Path) -> pd.DataFrame:
    """Load an existing CSV without modifying its source."""
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return pd.read_csv(path)


def load_json(path: Path) -> dict:
    """Load an existing JSON file without modifying its source."""
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def percent(value, digits=2):
    if pd.isna(value):
        return "N/A"
    return f"{value:.{digits}%}"


def number(value, digits=3):
    if pd.isna(value):
        return "N/A"
    return f"{value:.{digits}f}"


def validate_columns(df, required, label):
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(
            f"{label} is missing required columns: {missing}"
        )


# ============================================================
# LOAD FROZEN INPUTS
# ============================================================

st.title("Decision Support & Scenario Lab")
st.caption(
    "Adaptive Market Risk Intelligence System | Business evaluation v1"
)

st.info(
    "This page presents saved historical evaluation and sensitivity "
    "results. It is a research decision-support tool, not a live trading "
    "system or deployment approval."
)

try:
    evaluation = load_csv(EVALUATION_FILE)
    summary = load_json(SUMMARY_FILE)
    policy = load_json(POLICY_FILE)
    transaction_costs = load_csv(TRANSACTION_COST_FILE)

    robustness = (
        load_csv(ROBUSTNESS_FILE)
        if ROBUSTNESS_FILE.exists()
        else None
    )

except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
    st.error(f"Could not load the required saved inputs: {exc}")
    st.stop()


validate_columns(
    evaluation,
    [
        "Date",
        "Risk_Regime",
        "Portfolio_Exposure",
        "Static_Return",
        "Adaptive_Return",
        "Static_Wealth",
        "Adaptive_Wealth",
        "Forecasted_Volatility",
    ],
    "Business evaluation",
)

validate_columns(
    transaction_costs,
    [
        "Date",
        "Strategy",
        "Transaction_Cost_bps",
        "Net_Return",
        "Net_Wealth",
    ],
    "Transaction-cost analysis",
)

evaluation["Date"] = pd.to_datetime(
    evaluation["Date"], errors="coerce"
)
transaction_costs["Date"] = pd.to_datetime(
    transaction_costs["Date"], errors="coerce"
)

evaluation = evaluation.dropna(subset=["Date"]).sort_values("Date")
transaction_costs = transaction_costs.dropna(
    subset=["Date"]
).sort_values("Date")

if evaluation.empty or transaction_costs.empty:
    st.error("One or more required datasets contain no usable observations.")
    st.stop()


# ============================================================
# EVALUATION CONTEXT
# ============================================================

period = summary.get("evaluation_period", {})
static = summary.get("static_strategy", {})
adaptive = summary.get("adaptive_strategy", {})
impact = summary.get("business_impact", {})

st.subheader("Evaluation context")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Evaluation observations", f"{len(evaluation):,}")

with c2:
    st.metric(
        "Evaluation start",
        str(period.get("start", evaluation["Date"].min().date())),
    )

with c3:
    st.metric(
        "Evaluation end",
        str(period.get("end", evaluation["Date"].max().date())),
    )

with c4:
    st.metric(
        "Policy status",
        str(policy.get("policy_status", "Unknown")),
    )

st.caption(
    f"Forecast source: {policy.get('forecast_source_model', 'Not specified')} "
    f"| Research version: {policy.get('research_version', 'Not specified')} "
    f"| Evaluation period used for policy calibration: "
    f"{policy.get('evaluation_period_used_for_policy_calibration', 'Unknown')}"
)


# ============================================================
# SECTION 1 — STATIC VS ADAPTIVE PERFORMANCE
# ============================================================

st.divider()
st.subheader("1. Static vs Adaptive Strategy")

st.write(
    "The following figures come from the saved business evaluation summary. "
    "They describe the historical evaluation period only."
)

metric_cols = st.columns(4)

with metric_cols[0]:
    st.metric(
        "Static compounded return",
        percent(static.get("compounded_return", float("nan"))),
    )
    st.metric(
        "Adaptive compounded return",
        percent(adaptive.get("compounded_return", float("nan"))),
        delta=percent(
            impact.get("compounded_return_advantage", float("nan"))
        ),
        help="Adaptive minus static compounded return.",
    )

with metric_cols[1]:
    st.metric(
        "Static annualized volatility",
        percent(static.get("annualized_volatility", float("nan"))),
    )
    st.metric(
        "Adaptive annualized volatility",
        percent(adaptive.get("annualized_volatility", float("nan"))),
        delta=percent(
            -impact.get("volatility_reduction", float("nan"))
        ),
        delta_color="inverse",
        help="A negative delta indicates lower volatility for adaptive.",
    )

with metric_cols[2]:
    st.metric(
        "Static maximum drawdown",
        percent(static.get("maximum_drawdown", float("nan"))),
    )
    st.metric(
        "Adaptive maximum drawdown",
        percent(adaptive.get("maximum_drawdown", float("nan"))),
        delta=percent(
            impact.get("drawdown_improvement", float("nan"))
        ),
        help="Drawdown improvement is expressed in percentage points.",
    )

with metric_cols[3]:
    st.metric(
        "Static terminal wealth",
        number(static.get("terminal_wealth", float("nan")), 4),
    )
    st.metric(
        "Adaptive terminal wealth",
        number(adaptive.get("terminal_wealth", float("nan")), 4),
        delta=number(
            adaptive.get("terminal_wealth", float("nan"))
            - static.get("terminal_wealth", float("nan")),
            4,
        ),
        help="Starting wealth is represented by 1.0.",
    )


# Saved wealth paths
wealth_long = evaluation[
    ["Date", "Static_Wealth", "Adaptive_Wealth"]
].melt(
    id_vars="Date",
    var_name="Strategy",
    value_name="Wealth",
)

wealth_long["Strategy"] = wealth_long["Strategy"].map(
    {
        "Static_Wealth": "Static",
        "Adaptive_Wealth": "Adaptive",
    }
)

fig_wealth = px.line(
    wealth_long,
    x="Date",
    y="Wealth",
    color="Strategy",
    title="Saved evaluation-period wealth paths",
    labels={
        "Date": "Date",
        "Wealth": "Wealth index (starting near 1.0)",
        "Strategy": "Strategy",
    },
)
fig_wealth.add_hline(
    y=1.0,
    line_dash="dash",
    annotation_text="Starting wealth reference",
)
fig_wealth.update_layout(legend_title_text="Strategy")
st.plotly_chart(fig_wealth, use_container_width=True)

comparison = pd.DataFrame(
    {
        "Metric": [
            "Arithmetic return",
            "Compounded return",
            "Terminal wealth",
            "Maximum drawdown",
            "Annualized volatility",
            "Annualized downside deviation",
            "Sharpe ratio (zero risk-free rate)",
            "Negative-return observations",
        ],
        "Static": [
            static.get("arithmetic_return"),
            static.get("compounded_return"),
            static.get("terminal_wealth"),
            static.get("maximum_drawdown"),
            static.get("annualized_volatility"),
            static.get("annualized_downside_deviation"),
            static.get("sharpe_ratio"),
            static.get("negative_return_observations"),
        ],
        "Adaptive": [
            adaptive.get("arithmetic_return"),
            adaptive.get("compounded_return"),
            adaptive.get("terminal_wealth"),
            adaptive.get("maximum_drawdown"),
            adaptive.get("annualized_volatility"),
            adaptive.get("annualized_downside_deviation"),
            adaptive.get("sharpe_ratio"),
            adaptive.get("negative_return_observations"),
        ],
    }
)

st.markdown("**Detailed saved metrics**")
st.dataframe(
    comparison,
    hide_index=True,
    use_container_width=True,
)


# ============================================================
# SECTION 2 — RISK REGIME ANALYSIS
# ============================================================

st.divider()
st.subheader("2. Risk-Regime Analysis")

st.write(
    "Regime-level figures below are taken from the saved evaluation summary. "
    "They describe how the frozen policy behaved in each observed regime."
)

regime_records = summary.get("regime_summary", [])

if regime_records:
    regimes = pd.DataFrame(regime_records)

    expected_regime_columns = [
        "Risk_Regime",
        "Observations",
        "Average_Forecasted_Volatility",
        "Average_Exposure",
        "Static_Return",
        "Adaptive_Return",
        "Protection_Benefit",
    ]

    validate_columns(
        regimes,
        expected_regime_columns,
        "Regime summary",
    )

    regime_order = ["Low", "Normal", "Elevated", "High", "Extreme"]
    regimes["Risk_Regime"] = pd.Categorical(
        regimes["Risk_Regime"],
        categories=regime_order,
        ordered=True,
    )
    regimes = regimes.sort_values("Risk_Regime")

    left, right = st.columns(2)

    with left:
        fig_exposure = px.bar(
            regimes,
            x="Risk_Regime",
            y="Average_Exposure",
            title="Average portfolio exposure by risk regime",
            labels={
                "Risk_Regime": "Risk regime",
                "Average_Exposure": "Average exposure",
            },
            text="Average_Exposure",
        )
        fig_exposure.update_yaxes(
            tickformat=".0%",
            range=[0, 1.05],
        )
        st.plotly_chart(fig_exposure, use_container_width=True)

    with right:
        regime_returns = regimes.melt(
            id_vars="Risk_Regime",
            value_vars=["Static_Return", "Adaptive_Return"],
            var_name="Strategy",
            value_name="Return_Contribution",
        )
        regime_returns["Strategy"] = regime_returns["Strategy"].map(
            {
                "Static_Return": "Static",
                "Adaptive_Return": "Adaptive",
            }
        )

        fig_regime_returns = px.bar(
            regime_returns,
            x="Risk_Regime",
            y="Return_Contribution",
            color="Strategy",
            barmode="group",
            title="Sum of daily returns within each regime",
            labels={
                "Risk_Regime": "Risk regime",
                "Return_Contribution": "Sum of daily returns",
                "Strategy": "Strategy",
            },
        )
        fig_regime_returns.update_yaxes(tickformat=".1%")
        st.plotly_chart(fig_regime_returns, use_container_width=True)

    regime_display = regimes.copy()
    regime_display["Average_Forecasted_Volatility"] = (
        regime_display["Average_Forecasted_Volatility"].map(percent)
    )
    regime_display["Average_Exposure"] = (
        regime_display["Average_Exposure"].map(percent)
    )

    for col in [
        "Static_Return",
        "Adaptive_Return",
        "Protection_Benefit",
    ]:
        regime_display[col] = regime_display[col].map(percent)

    st.markdown("**Regime-level summary**")
    st.dataframe(
        regime_display,
        hide_index=True,
        use_container_width=True,
    )

    avg_exposure = impact.get("average_exposure")
    high_extreme_share = impact.get("high_extreme_share")

    a, b, c = st.columns(3)

    with a:
        st.metric("Average adaptive exposure", percent(avg_exposure))

    with b:
        st.metric(
            "High + Extreme observations",
            f"{impact.get('high_extreme_observations', 'N/A')}",
        )

    with c:
        st.metric(
            "High + Extreme share",
            percent(high_extreme_share),
        )

else:
    st.warning("No saved regime summary was found in the evaluation JSON.")


# ============================================================
# SECTION 3 — FROZEN POLICY
# ============================================================

st.divider()
st.subheader("3. Frozen Risk Policy")

thresholds = policy.get("thresholds", {})
exposure_policy = policy.get("exposure_policy", {})

st.write(
    "The thresholds below are the saved policy settings. This page does not "
    "recalibrate them or create a new trading rule."
)

threshold_rows = []
for regime, threshold in thresholds.items():
    threshold_rows.append(
        {
            "Threshold label": regime,
            "Forecasted volatility threshold": threshold,
            "Threshold (%)": percent(threshold),
        }
    )

if threshold_rows:
    st.dataframe(
        pd.DataFrame(threshold_rows),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.warning("No policy thresholds were found.")

exposure_rows = [
    {
        "Risk regime": regime,
        "Policy exposure": exposure,
        "Policy exposure (%)": percent(exposure),
    }
    for regime, exposure in exposure_policy.items()
]

if exposure_rows:
    st.markdown("**Saved regime-to-exposure policy**")
    st.dataframe(
        pd.DataFrame(exposure_rows),
        hide_index=True,
        use_container_width=True,
    )

st.caption(
    "Policy calibration period: "
    f"{policy.get('development_period', {}).get('start', 'N/A')} to "
    f"{policy.get('development_period', {}).get('end', 'N/A')}. "
    "The saved policy states that the evaluation period was not used for "
    "policy calibration."
)


# ============================================================
# SECTION 4 — TRANSACTION-COST SENSITIVITY
# ============================================================

st.divider()
st.subheader("4. Transaction-Cost Sensitivity")

st.write(
    "This section uses the saved transaction-cost analysis. Results depend "
    "on the cost assumptions, saved turnover series and the evaluation "
    "period; they are not forecasts of future net performance."
)

available_costs = sorted(
    pd.to_numeric(
        transaction_costs["Transaction_Cost_bps"],
        errors="coerce",
    ).dropna().unique().tolist()
)

available_strategies = sorted(
    transaction_costs["Strategy"].dropna().astype(str).unique().tolist()
)

if not available_costs or not available_strategies:
    st.warning("The transaction-cost file has no usable cost scenarios.")
else:
    selected_cost = st.selectbox(
        "Cost scenario for wealth-path chart (basis points)",
        options=available_costs,
        index=0,
        format_func=lambda value: f"{value:g} bps",
    )

    cost_view = transaction_costs[
        transaction_costs["Transaction_Cost_bps"] == selected_cost
    ].copy()

    fig_cost_wealth = px.line(
        cost_view,
        x="Date",
        y="Net_Wealth",
        color="Strategy",
        title=f"Net wealth paths at {selected_cost:g} bps",
        labels={
            "Date": "Date",
            "Net_Wealth": "Net wealth index",
            "Strategy": "Strategy",
        },
    )
    fig_cost_wealth.add_hline(
        y=1.0,
        line_dash="dash",
        annotation_text="Starting wealth reference",
    )
    st.plotly_chart(fig_cost_wealth, use_container_width=True)

    # Terminal wealth is the last saved wealth value for each strategy
    # within each cost scenario.
    terminal_rows = []

    for (cost_bps, strategy_name), group in transaction_costs.groupby(
        ["Transaction_Cost_bps", "Strategy"],
        dropna=True,
    ):
        group = group.sort_values("Date")
        last_row = group.iloc[-1]

        terminal_wealth = pd.to_numeric(
            pd.Series([last_row["Net_Wealth"]]),
            errors="coerce",
        ).iloc[0]

        terminal_rows.append(
            {
                "Transaction cost (bps)": cost_bps,
                "Strategy": strategy_name,
                "Observations": len(group),
                "Terminal net wealth": terminal_wealth,
                "Net compounded return": terminal_wealth - 1
                if pd.notna(terminal_wealth)
                else float("nan"),
            }
        )

    terminal_table = pd.DataFrame(terminal_rows).sort_values(
        ["Transaction cost (bps)", "Strategy"]
    )

    terminal_chart = px.line(
        terminal_table,
        x="Transaction cost (bps)",
        y="Net compounded return",
        color="Strategy",
        markers=True,
        title="Net compounded return across saved cost scenarios",
        labels={
            "Transaction cost (bps)": "Transaction cost (bps)",
            "Net compounded return": "Net compounded return",
            "Strategy": "Strategy",
        },
    )
    terminal_chart.update_yaxes(tickformat=".1%")
    st.plotly_chart(terminal_chart, use_container_width=True)

    terminal_display = terminal_table.copy()
    terminal_display["Terminal net wealth"] = (
        terminal_display["Terminal net wealth"].map(number)
    )
    terminal_display["Net compounded return"] = (
        terminal_display["Net compounded return"].map(percent)
    )

    st.markdown("**Terminal outcomes by saved cost scenario**")
    st.dataframe(
        terminal_display,
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "The terminal outcome is taken from the last saved Net_Wealth "
        "observation for each strategy and cost scenario. No new transaction "
        "costs are estimated by this dashboard."
    )


# ============================================================
# SECTION 5 — ROBUSTNESS SUMMARY
# ============================================================

st.divider()
st.subheader("5. Saved Robustness Results")

if robustness is not None and not robustness.empty:
    preferred_columns = [
        "scenario",
        "scenario_type",
        "start_date",
        "end_date",
        "observations",
        "strategy",
        "mean_adaptive_exposure",
        "compounded_return",
        "annualized_volatility",
        "maximum_drawdown",
        "negative_return_days",
    ]

    display_columns = [
        col for col in preferred_columns if col in robustness.columns
    ]

    scenario_values = sorted(
        robustness["scenario"].dropna().astype(str).unique().tolist()
    ) if "scenario" in robustness.columns else []

    if scenario_values:
        selected_scenario = st.selectbox(
            "Robustness scenario",
            options=scenario_values,
        )
        robustness_view = robustness[
            robustness["scenario"].astype(str) == selected_scenario
        ].copy()
    else:
        robustness_view = robustness.copy()

    st.dataframe(
        robustness_view[display_columns],
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "These rows are displayed from the saved robustness comparison. "
        "Scenario labels and values are not recomputed here."
    )
else:
    st.info(
        "The saved robustness comparison file is not available. "
        "The main evaluation and transaction-cost sections remain usable."
    )


# ============================================================
# SECTION 6 — GOVERNANCE AND LIMITATIONS
# ============================================================

st.divider()
st.subheader("6. Governance, Interpretation & Limitations")

st.warning(
    "**Not approved for live deployment.** The saved governance record "
    "previously indicated that deployment was not approved. This dashboard "
    "does not change that status."
)

st.markdown(
    """
    **Interpretation guidelines**

    - The evaluation is historical and covers a finite out-of-sample period.
    - The adaptive strategy's lower historical drawdown and volatility do
      not guarantee that the same benefits will persist.
    - Transaction-cost results depend on the assumptions and turnover
      represented in the saved cost-analysis file.
    - The frozen thresholds and exposure policy are shown as recorded;
      this page does not optimize or recalibrate them.
    - No live market feed, order routing or automated trade execution is
      performed by this page.
    - The adaptive policy assumes uninvested cash earns 0%, as recorded in
      the saved evaluation methodology.
    """
)

with st.expander("View data sources used by this page"):
    st.write(f"Evaluation CSV: `{EVALUATION_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(f"Evaluation summary: `{SUMMARY_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(f"Frozen policy: `{POLICY_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(
        "Transaction costs: "
        f"`{TRANSACTION_COST_FILE.relative_to(PROJECT_ROOT)}`"
    )
    if robustness is not None:
        st.write(
            f"Robustness comparison: `{ROBUSTNESS_FILE.relative_to(PROJECT_ROOT)}`"
        )

st.caption(
    "AMRIS | Decision Support & Scenario Lab | Read-only presentation of "
    "saved research outputs"
)
