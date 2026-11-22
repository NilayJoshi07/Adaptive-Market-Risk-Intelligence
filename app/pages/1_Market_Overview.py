
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# AMRIS — MARKET RISK OVERVIEW
# Reads existing datasets only.
# ============================================================

st.set_page_config(
    page_title="Market Risk Overview | AMRIS",
    page_icon="📊",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

NIFTY_FILE = PROJECT_ROOT / "data" / "processed" / "nifty50_clean.csv"

VIX_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "india_vix_clean_daily_2018-01-01_2026-09-22.csv"
)

DECISION_FILE = (
    PROJECT_ROOT
    / "data"
    / "business_decision"
    / "v1"
    / "business_decision_data.csv"
)


@st.cache_data
def load_csv(path_string, modified_time):
    df = pd.read_csv(path_string)

    if "Date" not in df.columns:
        raise ValueError(f"Date column missing in {path_string}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    if df["Date"].isna().any():
        raise ValueError(f"Invalid dates found in {path_string}")

    if df["Date"].duplicated().any():
        raise ValueError(f"Duplicate dates found in {path_string}")

    return df.sort_values("Date").reset_index(drop=True)


# ------------------------------------------------------------
# Load source datasets
# ------------------------------------------------------------

st.title("Market Risk Overview")
st.caption(
    "Adaptive Market Risk Intelligence System | "
    "Historical market monitoring and risk decision support"
)

st.info(
    "This dashboard uses saved historical datasets. "
    "The latest displayed observation is not necessarily "
    "the current live market value."
)

for path in [NIFTY_FILE, VIX_FILE, DECISION_FILE]:
    if not path.exists():
        st.error(f"Required data file not found: {path}")
        st.stop()

try:
    nifty = load_csv(str(NIFTY_FILE), NIFTY_FILE.stat().st_mtime)
    vix = load_csv(str(VIX_FILE), VIX_FILE.stat().st_mtime)
    decisions = load_csv(
        str(DECISION_FILE),
        DECISION_FILE.stat().st_mtime,
    )
except Exception as exc:
    st.error(f"Unable to load dashboard data: {exc}")
    st.stop()


# ------------------------------------------------------------
# Validate required columns
# ------------------------------------------------------------

required_nifty = {"Date", "Open", "High", "Low", "Close", "Volume"}
required_vix = {"Date", "India_VIX"}
required_decisions = {
    "Date",
    "Forecasted_Volatility",
    "Risk_Regime",
    "Portfolio_Exposure",
}

for name, df, required in [
    ("NIFTY", nifty, required_nifty),
    ("India VIX", vix, required_vix),
    ("Business decisions", decisions, required_decisions),
]:
    missing = required.difference(df.columns)
    if missing:
        st.error(f"{name} data is missing columns: {sorted(missing)}")
        st.stop()

for col in ["Open", "High", "Low", "Close", "Volume"]:
    nifty[col] = pd.to_numeric(nifty[col], errors="coerce")

vix["India_VIX"] = pd.to_numeric(vix["India_VIX"], errors="coerce")

for col in ["Forecasted_Volatility", "Portfolio_Exposure"]:
    decisions[col] = pd.to_numeric(decisions[col], errors="coerce")

if nifty[["Open", "High", "Low", "Close"]].isna().any().any():
    st.error("NIFTY price data contains missing or invalid price values.")
    st.stop()

if not np.isfinite(
    nifty[["Open", "High", "Low", "Close"]].to_numpy(dtype=float)
).all():
    st.error("NIFTY price data contains non-finite values.")
    st.stop()

if vix["India_VIX"].dropna().empty:
    st.error("No valid India VIX observations are available.")
    st.stop()

if decisions.empty:
    st.error("The business-decision dataset is empty.")
    st.stop()


# ------------------------------------------------------------
# Latest observations
# ------------------------------------------------------------

latest_nifty = nifty.dropna(subset=["Close"]).iloc[-1]
latest_vix = vix.dropna(subset=["India_VIX"]).iloc[-1]
latest_decision = decisions.dropna(
    subset=["Forecasted_Volatility", "Portfolio_Exposure"]
).iloc[-1]

nifty_previous = nifty.loc[
    nifty["Date"] < latest_nifty["Date"]
].dropna(subset=["Close"])

if not nifty_previous.empty:
    previous_close = float(nifty_previous.iloc[-1]["Close"])
    nifty_change = float(latest_nifty["Close"]) / previous_close - 1
else:
    nifty_change = None

nifty_date = latest_nifty["Date"]
vix_date = latest_vix["Date"]
decision_date = latest_decision["Date"]


# ------------------------------------------------------------
# Market snapshot
# ------------------------------------------------------------

st.subheader("Latest available market snapshot")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "NIFTY 50 Close",
    f"{latest_nifty['Close']:,.2f}",
    delta=(
        f"{nifty_change:+.2%}"
        if nifty_change is not None
        else None
    ),
)

c2.metric(
    "India VIX",
    f"{latest_vix['India_VIX']:.2f}",
)

c3.metric(
    "Forecasted Volatility",
    f"{latest_decision['Forecasted_Volatility']:.2%}",
)

c4.metric(
    "Portfolio Exposure",
    f"{latest_decision['Portfolio_Exposure']:.0%}",
)

st.caption(
    f"NIFTY date: {nifty_date:%d %b %Y} | "
    f"India VIX date: {vix_date:%d %b %Y} | "
    f"Risk decision date: {decision_date:%d %b %Y}"
)


# ------------------------------------------------------------
# Risk regime and forecast status
# ------------------------------------------------------------

st.subheader("Risk decision snapshot")

r1, r2, r3 = st.columns(3)

with r1:
    st.markdown("**Latest saved risk regime**")
    st.subheader(str(latest_decision["Risk_Regime"]))

with r2:
    st.markdown("**Forecast source**")
    st.write("EGARCH-t with India VIX, as saved in the decision data")

with r3:
    st.markdown("**Decision observation**")
    st.write(decision_date.strftime("%d %B %Y"))

if decision_date != nifty_date:
    st.warning(
        "The latest risk-decision date differs from the latest "
        "NIFTY date. Interpret the snapshots using their displayed dates."
    )


# ------------------------------------------------------------
# Date filter
# ------------------------------------------------------------

st.subheader("Historical market trends")

latest_market_date = max(nifty["Date"].max(), vix["Date"].max())
default_start = max(
    min(nifty["Date"].min(), vix["Date"].min()),
    latest_market_date - pd.Timedelta(days=365),
)

left, right = st.columns(2)

with left:
    date_range = st.date_input(
        "Select trend date range",
        value=(default_start.date(), latest_market_date.date()),
        min_value=min(nifty["Date"].min(), vix["Date"].min()).date(),
        max_value=latest_market_date.date(),
        key="overview_date_range",
    )

with right:
    show_volume = st.checkbox(
        "Show NIFTY trading volume",
        value=False,
    )

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        st.warning("Choose a valid date range.")
        st.stop()
else:
    start_date = end_date = date_range

if start_date > end_date:
    st.warning("Start date must not be after end date.")
    st.stop()

nifty_filtered = nifty.loc[
    nifty["Date"].dt.date.between(start_date, end_date)
].copy()

vix_filtered = vix.loc[
    vix["Date"].dt.date.between(start_date, end_date)
].copy()

if nifty_filtered.empty or vix_filtered.empty:
    st.warning(
        "No data is available for one or both charts in this date range."
    )
    st.stop()


# ------------------------------------------------------------
# NIFTY price chart
# ------------------------------------------------------------

price_chart = px.line(
    nifty_filtered,
    x="Date",
    y="Close",
    title="NIFTY 50 — Closing Price",
    labels={
        "Date": "Date",
        "Close": "Closing Price",
    },
)

price_chart.update_layout(hovermode="x unified")

st.plotly_chart(price_chart, use_container_width=True)


# ------------------------------------------------------------
# India VIX chart
# ------------------------------------------------------------

vix_chart = px.line(
    vix_filtered,
    x="Date",
    y="India_VIX",
    title="India VIX — Market-Implied Volatility Index",
    labels={
        "Date": "Date",
        "India_VIX": "India VIX",
    },
)

vix_chart.update_layout(hovermode="x unified")

st.plotly_chart(vix_chart, use_container_width=True)


# ------------------------------------------------------------
# Optional volume chart
# ------------------------------------------------------------

if show_volume:
    volume_chart = px.bar(
        nifty_filtered,
        x="Date",
        y="Volume",
        title="NIFTY 50 — Trading Volume",
        labels={
            "Date": "Date",
            "Volume": "Volume",
        },
    )

    st.plotly_chart(volume_chart, use_container_width=True)


# ------------------------------------------------------------
# Risk regime history
# ------------------------------------------------------------

st.subheader("Historical risk regime")

decision_filtered = decisions.loc[
    decisions["Date"].dt.date.between(start_date, end_date)
].copy()

if not decision_filtered.empty:
    regime_chart = px.scatter(
        decision_filtered,
        x="Date",
        y="Forecasted_Volatility",
        color="Risk_Regime",
        hover_data=["Portfolio_Exposure"],
        title="Saved volatility forecasts by risk regime",
        labels={
            "Date": "Date",
            "Forecasted_Volatility": "Forecasted Volatility",
            "Risk_Regime": "Risk Regime",
            "Portfolio_Exposure": "Portfolio Exposure",
        },
    )

    regime_chart.update_yaxes(tickformat=".2%")
    regime_chart.update_layout(hovermode="x unified")

    st.plotly_chart(regime_chart, use_container_width=True)

    history = decision_filtered[
        [
            "Date",
            "Forecasted_Volatility",
            "Risk_Regime",
            "Portfolio_Exposure",
        ]
    ].sort_values("Date", ascending=False).head(10).copy()

    history["Date"] = history["Date"].dt.strftime("%Y-%m-%d")
    history["Forecasted_Volatility"] = history[
        "Forecasted_Volatility"
    ].map(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
    history["Portfolio_Exposure"] = history[
        "Portfolio_Exposure"
    ].map(lambda x: f"{x:.0%}" if pd.notna(x) else "N/A")

    st.markdown("**Latest saved risk decisions**")
    st.dataframe(history, use_container_width=True, hide_index=True)
else:
    st.info("No risk-decision observations exist in the selected period.")


# ------------------------------------------------------------
# Data freshness and governance
# ------------------------------------------------------------

st.subheader("Data freshness and source status")

status_data = pd.DataFrame(
    [
        {
            "Dataset": "NIFTY 50",
            "Rows": len(nifty),
            "First Date": nifty["Date"].min().date(),
            "Last Date": nifty["Date"].max().date(),
            "Source": "data/processed/nifty50_clean.csv",
        },
        {
            "Dataset": "India VIX",
            "Rows": len(vix),
            "First Date": vix["Date"].min().date(),
            "Last Date": vix["Date"].max().date(),
            "Source": (
                "data/processed/"
                "india_vix_clean_daily_2018-01-01_2026-09-22.csv"
            ),
        },
        {
            "Dataset": "Business decisions",
            "Rows": len(decisions),
            "First Date": decisions["Date"].min().date(),
            "Last Date": decisions["Date"].max().date(),
            "Source": (
                "data/business_decision/v1/"
                "business_decision_data.csv"
            ),
        },
    ]
)

st.dataframe(
    status_data,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "AMRIS research dashboard | Uses frozen saved datasets | "
    "No live market feed, model refitting, or automated trade execution."
)
