
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Rolling Risk Monitor | AMRIS",
    page_icon="📉",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RISK_FILE = (
    PROJECT_ROOT
    / "data"
    / "risk_outputs"
    / "v1"
    / "rolling_historical_risk_126d.csv"
)


@st.cache_data
def load_risk_data(file_path, modified_time):
    df = pd.read_csv(file_path, parse_dates=["Date"])

    required = {
        "Date",
        "Window_Start",
        "Window_End",
        "Window_Observations",
        "Strategy",
        "Confidence_Level",
        "Horizon",
        "VaR",
        "ES_CVaR",
        "Tail_Observations",
    }

    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"Missing CSV columns: {sorted(missing)}"
        )

    numeric = [
        "Window_Observations",
        "Confidence_Level",
        "VaR",
        "ES_CVaR",
        "Tail_Observations",
    ]

    for column in numeric:
        df[column] = pd.to_numeric(
            df[column], errors="raise"
        )

    if df.empty:
        raise ValueError("The risk CSV is empty.")

    if df["Date"].isna().any():
        raise ValueError("Invalid dates in the CSV.")

    if not np.isfinite(df[numeric].to_numpy(dtype=float)).all():
        raise ValueError("The CSV contains non-finite numeric values.")

    if df.duplicated(
        ["Date", "Strategy", "Confidence_Level"]
    ).any():
        raise ValueError("Duplicate risk records detected.")

    if not set(df["Strategy"].unique()).issubset(
        {"Static", "Adaptive"}
    ):
        raise ValueError("Unexpected strategy values.")

    if not set(df["Confidence_Level"].unique()).issubset(
        {0.95, 0.99}
    ):
        raise ValueError("Unexpected confidence levels.")

    if (df[["VaR", "ES_CVaR"]] < 0).any().any():
        raise ValueError("VaR and ES/CVaR must be non-negative.")

    return df.sort_values("Date").reset_index(drop=True)


st.title("Rolling Historical Risk Monitor")
st.caption(
    "Adaptive Market Risk Intelligence System | "
    "Historical tail-risk analysis"
)

st.markdown(
    """
    Compare historical downside risk under **Static** and
    **Adaptive** exposure strategies. Estimates use the saved
    rolling-risk dataset; this page does not refit models or
    regenerate risk outputs.
    """
)

if not RISK_FILE.exists():
    st.error(f"Risk output not found: {RISK_FILE}")
    st.stop()

try:
    risk = load_risk_data(
        str(RISK_FILE),
        RISK_FILE.stat().st_mtime,
    )
except Exception as exc:
    st.error(f"Unable to load the risk output: {exc}")
    st.stop()


# ------------------------------------------------------------
# Filters
# ------------------------------------------------------------

min_date = risk["Date"].min().date()
max_date = risk["Date"].max().date()

st.subheader("Filters")

c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="rolling_risk_dates",
    )

with c2:
    confidence_label = st.selectbox(
        "Confidence level",
        ["95%", "99%"],
    )

with c3:
    strategy_filter = st.selectbox(
        "Strategy",
        ["Static vs Adaptive", "Static", "Adaptive"],
    )

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        st.warning("Select a valid date range.")
        st.stop()
else:
    start_date = end_date = date_range

if start_date > end_date:
    st.warning("Start date must not be after end date.")
    st.stop()

confidence = 0.95 if confidence_label == "95%" else 0.99

filtered = risk.loc[
    risk["Date"].dt.date.between(start_date, end_date)
    & (risk["Confidence_Level"] == confidence)
].copy()

if strategy_filter != "Static vs Adaptive":
    filtered = filtered[
        filtered["Strategy"] == strategy_filter
    ]

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()


# ------------------------------------------------------------
# Latest estimates
# ------------------------------------------------------------

st.subheader(f"Latest available risk estimates — {confidence_label}")

latest_date = filtered["Date"].max()
latest = filtered.loc[filtered["Date"] == latest_date].copy()

st.caption(f"Latest selected date: {latest_date:%d %b %Y}")

if strategy_filter == "Static vs Adaptive":
    metric_columns = st.columns(4)

    for strategy, offset in [("Static", 0), ("Adaptive", 2)]:
        row = latest.loc[latest["Strategy"] == strategy]

        if row.empty:
            metric_columns[offset].metric(
                f"{strategy} VaR", "Not available"
            )
            metric_columns[offset + 1].metric(
                f"{strategy} ES/CVaR", "Not available"
            )
            continue

        row = row.iloc[0]

        metric_columns[offset].metric(
            f"{strategy} VaR",
            f"{row['VaR']:.2%}",
        )
        metric_columns[offset + 1].metric(
            f"{strategy} ES/CVaR",
            f"{row['ES_CVaR']:.2%}",
        )
else:
    row = latest.loc[latest["Strategy"] == strategy_filter]

    if not row.empty:
        row = row.iloc[0]
        m1, m2 = st.columns(2)
        m1.metric("Historical VaR", f"{row['VaR']:.2%}")
        m2.metric("Expected Shortfall", f"{row['ES_CVaR']:.2%}")


# ------------------------------------------------------------
# Rolling VaR
# ------------------------------------------------------------

st.subheader("Rolling Value at Risk (VaR)")

var_chart = px.line(
    filtered,
    x="Date",
    y="VaR",
    color="Strategy",
    labels={
        "Date": "Date",
        "VaR": "VaR (historical loss)",
        "Strategy": "Strategy",
    },
    title=f"{confidence_label} rolling historical VaR",
)

var_chart.update_yaxes(tickformat=".2%")
var_chart.update_layout(hovermode="x unified")

st.plotly_chart(var_chart, use_container_width=True)


# ------------------------------------------------------------
# Rolling Expected Shortfall
# ------------------------------------------------------------

st.subheader("Rolling Expected Shortfall (ES/CVaR)")

es_chart = px.line(
    filtered,
    x="Date",
    y="ES_CVaR",
    color="Strategy",
    labels={
        "Date": "Date",
        "ES_CVaR": "Expected Shortfall",
        "Strategy": "Strategy",
    },
    title=f"{confidence_label} rolling historical ES/CVaR",
)

es_chart.update_yaxes(tickformat=".2%")
es_chart.update_layout(hovermode="x unified")

st.plotly_chart(es_chart, use_container_width=True)


# ------------------------------------------------------------
# Comparison table
# ------------------------------------------------------------

st.subheader("Latest strategy comparison")

display = latest[
    [
        "Date",
        "Window_Start",
        "Window_End",
        "Window_Observations",
        "Strategy",
        "Confidence_Level",
        "Horizon",
        "VaR",
        "ES_CVaR",
        "Tail_Observations",
    ]
].copy()

display["Date"] = display["Date"].dt.strftime("%Y-%m-%d")
display["VaR"] = display["VaR"].map(lambda x: f"{x:.2%}")
display["ES_CVaR"] = display["ES_CVaR"].map(lambda x: f"{x:.2%}")
display["Confidence_Level"] = display["Confidence_Level"].map(
    lambda x: f"{x:.0%}"
)

st.dataframe(display, use_container_width=True, hide_index=True)


# ------------------------------------------------------------
# Methodology and limitations
# ------------------------------------------------------------

with st.expander("Methodology, assumptions and limitations"):
    st.markdown(
        """
        - **Window:** 126 prior observations, excluding the date
          being estimated.
        - **VaR:** Empirical quantile of historical losses.
        - **ES/CVaR:** Average loss among observations in the
          estimated tail, following the saved calculation.
        - **Static:** Market returns at 100% exposure.
        - **Adaptive:** Market returns scaled by the saved
          portfolio exposure; uninvested exposure is assumed to
          earn zero return in the underlying calculation.
        - **99% caution:** A 126-observation window contains very
          few observations in the 1% tail, so these estimates are
          particularly noisy.
        - Historical risk estimates are not guarantees of future
          losses or authorization for live trading.
        """
    )

st.caption(
    f"Source: {RISK_FILE.relative_to(PROJECT_ROOT)} | "
    f"Dataset dates: {min_date} to {max_date} | "
    f"Records: {len(risk):,}"
)
