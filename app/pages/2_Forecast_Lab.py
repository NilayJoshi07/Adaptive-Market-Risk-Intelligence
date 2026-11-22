
from pathlib import Path
import re

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# AMRIS — MULTI-MODEL VOLATILITY FORECAST LAB
# Reads frozen research outputs only.
# ============================================================

st.set_page_config(
    page_title="Volatility Forecast Lab | AMRIS",
    page_icon="📈",
    layout="wide",
)

ROOT = Path(__file__).resolve().parents[2]

FORECAST_FILE = (
    ROOT / "data" / "research_outputs" / "v1"
    / "oos_forecasts.csv"
)

PERFORMANCE_FILE = (
    ROOT / "data" / "research_outputs" / "v1"
    / "model_performance.csv"
)

MODEL_LABELS = {
    "Historical_20D": "Historical 20D",
    "EWMA": "EWMA",
    "GARCH_t": "GARCH-t",
    "GJR_GARCH_t": "GJR-GARCH-t",
    "EGARCH_t": "EGARCH-t",
    "Historical_20D_VIX": "Historical 20D + VIX",
    "EWMA_VIX": "EWMA + VIX",
    "EGARCH_t_VIX": "EGARCH-t + VIX",
}


def normalize_name(value):
    """Normalize model names for matching across saved files."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


@st.cache_data
def load_csv(path_string, modified_time):
    return pd.read_csv(path_string)


def format_pct(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.4%}"


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.title("Volatility Forecast Lab")
st.caption(
    "AMRIS | Out-of-sample forecasting research and model comparison"
)

st.info(
    "This page visualizes saved out-of-sample forecasts and saved "
    "performance metrics. It does not refit models or modify the "
    "research baseline."
)


# ------------------------------------------------------------
# Load the frozen outputs
# ------------------------------------------------------------

for path in [FORECAST_FILE, PERFORMANCE_FILE]:
    if not path.exists():
        st.error(f"Required research output not found: {path}")
        st.stop()

try:
    forecasts = load_csv(
        str(FORECAST_FILE),
        FORECAST_FILE.stat().st_mtime,
    )
    performance = load_csv(
        str(PERFORMANCE_FILE),
        PERFORMANCE_FILE.stat().st_mtime,
    )
except Exception as exc:
    st.error(f"Could not load research outputs: {exc}")
    st.stop()


# ------------------------------------------------------------
# Validate schemas
# ------------------------------------------------------------

required_forecast = {"Date", "Actual_Volatility"}
required_performance = {
    "Model", "MAE", "RMSE", "N", "OOS_Start", "OOS_End"
}

missing_forecast = required_forecast - set(forecasts.columns)
missing_performance = required_performance - set(performance.columns)

if missing_forecast:
    st.error(
        f"Forecast file missing columns: {sorted(missing_forecast)}"
    )
    st.stop()

if missing_performance:
    st.error(
        f"Performance file missing columns: {sorted(missing_performance)}"
    )
    st.stop()

forecasts["Date"] = pd.to_datetime(
    forecasts["Date"], errors="coerce"
)

if forecasts["Date"].isna().any():
    st.error("The forecast file contains invalid dates.")
    st.stop()

if forecasts["Date"].duplicated().any():
    st.error("The forecast file contains duplicate dates.")
    st.stop()

forecast_columns = [
    column for column in MODEL_LABELS
    if column in forecasts.columns
]

if not forecast_columns:
    st.error("None of the expected model forecast columns were found.")
    st.stop()

numeric_forecast_columns = ["Actual_Volatility"] + forecast_columns

for column in numeric_forecast_columns:
    forecasts[column] = pd.to_numeric(
        forecasts[column], errors="coerce"
    )

valid_numeric = forecasts[numeric_forecast_columns].dropna()

if not valid_numeric.empty:
    if not np.isfinite(valid_numeric.to_numpy(dtype=float)).all():
        st.error("Non-finite forecast values were detected.")
        st.stop()

performance["MAE"] = pd.to_numeric(
    performance["MAE"], errors="coerce"
)
performance["RMSE"] = pd.to_numeric(
    performance["RMSE"], errors="coerce"
)
performance["N"] = pd.to_numeric(
    performance["N"], errors="coerce"
)
performance["OOS_Start"] = pd.to_datetime(
    performance["OOS_Start"], errors="coerce"
)
performance["OOS_End"] = pd.to_datetime(
    performance["OOS_End"], errors="coerce"
)

if performance[["MAE", "RMSE"]].isna().any().any():
    st.error("The performance table contains invalid MAE or RMSE values.")
    st.stop()

if not np.isfinite(
    performance[["MAE", "RMSE"]].to_numpy(dtype=float)
).all():
    st.error("The performance table contains non-finite metrics.")
    st.stop()


# Match saved performance labels to the forecast column names.
forecast_lookup = {
    normalize_name(column): column
    for column in forecast_columns
}

performance["Model_Key"] = performance["Model"].map(normalize_name)

performance["Display_Model"] = performance["Model_Key"].map(
    lambda key: next(
        (
            MODEL_LABELS[column]
            for column in forecast_columns
            if normalize_name(column) == key
        ),
        None,
    )
)

# Preserve unmatched model rows in the performance table.
performance["Display_Model"] = performance["Display_Model"].fillna(
    performance["Model"].astype(str)
)


# ------------------------------------------------------------
# Dataset summary
# ------------------------------------------------------------

start_date = forecasts["Date"].min()
end_date = forecasts["Date"].max()

m1, m2, m3, m4 = st.columns(4)

m1.metric("OOS observations", f"{len(forecasts):,}")
m2.metric("Forecast models available", str(len(forecast_columns)))
m3.metric("OOS start", start_date.strftime("%d %b %Y"))
m4.metric("OOS end", end_date.strftime("%d %b %Y"))

st.divider()


# ============================================================
# SECTION 1 — SAVED MODEL PERFORMANCE
# ============================================================

st.header("1. Model accuracy comparison")

st.write(
    "Compare the saved out-of-sample MAE and RMSE metrics. "
    "Lower values indicate smaller errors under the corresponding metric."
)

perf_display = performance[
    [
        "Display_Model",
        "MAE",
        "RMSE",
        "N",
        "OOS_Start",
        "OOS_End",
    ]
].copy()

perf_display = perf_display.sort_values("MAE").reset_index(drop=True)

perf_table = perf_display.copy()
perf_table["MAE"] = perf_table["MAE"].map(format_pct)
perf_table["RMSE"] = perf_table["RMSE"].map(format_pct)
perf_table["N"] = perf_table["N"].map(
    lambda value: f"{int(value):,}" if pd.notna(value) else "N/A"
)
perf_table["OOS_Start"] = perf_table["OOS_Start"].dt.strftime("%Y-%m-%d")
perf_table["OOS_End"] = perf_table["OOS_End"].dt.strftime("%Y-%m-%d")

perf_table = perf_table.rename(
    columns={
        "Display_Model": "Model",
        "OOS_Start": "OOS Start",
        "OOS_End": "OOS End",
    }
)

st.dataframe(
    perf_table,
    use_container_width=True,
    hide_index=True,
)

left, right = st.columns(2)

with left:
    mae_chart = px.bar(
        perf_display,
        x="Display_Model",
        y="MAE",
        title="Mean Absolute Error (MAE)",
        labels={
            "Display_Model": "Model",
            "MAE": "MAE",
        },
    )
    mae_chart.update_yaxes(tickformat=".2%")
    mae_chart.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(mae_chart, use_container_width=True)

with right:
    rmse_chart = px.bar(
        perf_display,
        x="Display_Model",
        y="RMSE",
        title="Root Mean Squared Error (RMSE)",
        labels={
            "Display_Model": "Model",
            "RMSE": "RMSE",
        },
    )
    rmse_chart.update_yaxes(tickformat=".2%")
    rmse_chart.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(rmse_chart, use_container_width=True)

with st.expander("How to interpret MAE and RMSE"):
    st.markdown(
        """
        - **MAE** summarizes the average magnitude of forecast errors.
        - **RMSE** penalizes larger errors more strongly than MAE.
        - These metrics are read from the saved performance file; this
          page does not recompute or overwrite the official results.
        - Compare results only with attention to the recorded evaluation
          periods, sample sizes, target definition and information set.
        """
    )


st.divider()


# ============================================================
# SECTION 2 — MULTI-MODEL FORECAST COMPARISON
# ============================================================

st.header("2. Actual volatility versus model forecasts")

st.write(
    "Select the models you want to compare. The chart uses the saved "
    "values aligned by date in the out-of-sample forecast file."
)

default_models = [
    model for model in [
        "Historical_20D",
        "EWMA",
        "GARCH_t",
        "GJR_GARCH_t",
        "EGARCH_t",
        "Historical_20D_VIX",
        "EWMA_VIX",
        "EGARCH_t_VIX",
    ]
    if model in forecast_columns
]

selected_models = st.multiselect(
    "Forecast models to display",
    options=forecast_columns,
    default=default_models,
    format_func=lambda model: MODEL_LABELS.get(model, model),
    key="forecast_model_selection",
)

c1, c2 = st.columns(2)

with c1:
    chart_start = st.date_input(
        "Chart start date",
        value=start_date.date(),
        min_value=start_date.date(),
        max_value=end_date.date(),
        key="forecast_chart_start",
    )

with c2:
    chart_end = st.date_input(
        "Chart end date",
        value=end_date.date(),
        min_value=start_date.date(),
        max_value=end_date.date(),
        key="forecast_chart_end",
    )

if chart_start > chart_end:
    st.warning("The chart start date must not be after the end date.")
    st.stop()

if not selected_models:
    st.warning("Select at least one forecast model.")
else:
    chart_data = forecasts.loc[
        forecasts["Date"].dt.date.between(chart_start, chart_end),
        ["Date", "Actual_Volatility"] + selected_models,
    ].copy()

    long_data = chart_data.melt(
        id_vars=["Date"],
        value_vars=["Actual_Volatility"] + selected_models,
        var_name="Series",
        value_name="Volatility",
    )

    long_data["Series"] = long_data["Series"].map(
        lambda value: (
            "Actual volatility"
            if value == "Actual_Volatility"
            else MODEL_LABELS.get(value, value)
        )
    )

    long_data = long_data.dropna(subset=["Volatility"])

    forecast_chart = px.line(
        long_data,
        x="Date",
        y="Volatility",
        color="Series",
        title="Saved actual and forecast volatility series",
        labels={
            "Date": "Date",
            "Volatility": "Volatility",
            "Series": "Series",
        },
    )

    forecast_chart.update_yaxes(tickformat=".2%")
    forecast_chart.update_layout(
        hovermode="x unified",
        legend_title_text="Series",
    )

    st.plotly_chart(forecast_chart, use_container_width=True)


st.divider()


# ============================================================
# SECTION 3 — FORECAST ERROR BEHAVIOUR
# ============================================================

st.header("3. Forecast error behaviour over time")

st.write(
    "Inspect how absolute errors vary through the evaluation period. "
    "These error series are calculated from the saved actual and forecast "
    "columns for visualization; official MAE/RMSE values remain sourced "
    "from the saved performance table."
)

if selected_models:
    error_data = forecasts.loc[
        forecasts["Date"].dt.date.between(chart_start, chart_end),
        ["Date", "Actual_Volatility"] + selected_models,
    ].copy()

    error_long_rows = []

    for model in selected_models:
        pair = error_data[["Date", "Actual_Volatility", model]].dropna()

        if pair.empty:
            continue

        pair["Absolute_Error"] = (
            pair[model] - pair["Actual_Volatility"]
        ).abs()

        pair["Model"] = MODEL_LABELS.get(model, model)

        error_long_rows.append(
            pair[["Date", "Model", "Absolute_Error"]]
        )

    if error_long_rows:
        errors_long = pd.concat(
            error_long_rows, ignore_index=True
        )

        error_chart = px.line(
            errors_long,
            x="Date",
            y="Absolute_Error",
            color="Model",
            title="Absolute forecast error by model",
            labels={
                "Date": "Date",
                "Absolute_Error": "Absolute error",
                "Model": "Model",
            },
        )

        error_chart.update_yaxes(tickformat=".2%")
        error_chart.update_layout(hovermode="x unified")

        st.plotly_chart(error_chart, use_container_width=True)

        error_summary = (
            errors_long.groupby("Model", as_index=False)
            .agg(
                Mean_Absolute_Error=("Absolute_Error", "mean"),
                Median_Absolute_Error=("Absolute_Error", "median"),
                Observations=("Absolute_Error", "count"),
            )
            .sort_values("Mean_Absolute_Error")
        )

        st.markdown("**Descriptive error summary for the selected date range**")

        summary_display = error_summary.copy()
        summary_display["Mean_Absolute_Error"] = (
            summary_display["Mean_Absolute_Error"].map(format_pct)
        )
        summary_display["Median_Absolute_Error"] = (
            summary_display["Median_Absolute_Error"].map(format_pct)
        )

        summary_display = summary_display.rename(
            columns={
                "Mean_Absolute_Error": "Mean absolute error",
                "Median_Absolute_Error": "Median absolute error",
                "Observations": "Observations",
            }
        )

        st.dataframe(
            summary_display,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("No valid forecast-error observations in this range.")


st.divider()


# ============================================================
# SECTION 4 — MODEL AND DATA DETAILS
# ============================================================

st.header("4. Research coverage and limitations")

with st.expander("Forecast columns available in the saved file"):
    coverage = pd.DataFrame(
        [
            {
                "Forecast column": column,
                "Dashboard label": MODEL_LABELS.get(column, column),
                "Non-missing observations": int(
                    forecasts[column].notna().sum()
                ),
            }
            for column in forecast_columns
        ]
    )

    st.dataframe(
        coverage,
        use_container_width=True,
        hide_index=True,
    )

with st.expander("Research interpretation and governance"):
    st.markdown(
        """
        **Research comparisons**

        - Historical 20-day and EWMA are benchmark approaches.
        - GARCH-t, GJR-GARCH-t and EGARCH-t represent different
          conditional-volatility specifications.
        - The VIX-enhanced variants let you compare the saved forecasts
          that incorporate India VIX with the other available variants.

        **Important qualifications**

        - The dashboard presents the frozen saved outputs; it does not
          establish that any model is universally best.
        - Forecast alignment and target construction must be interpreted
          according to the frozen research methodology.
        - The error summary for a user-selected date range is descriptive
          and should not be mistaken for the official full-period metrics.
        - This is a research and decision-support tool, not a live
          trading system or evidence of deployment approval.
        """
    )

st.caption(
    "Sources: data/research_outputs/v1/oos_forecasts.csv and "
    "data/research_outputs/v1/model_performance.csv. "
    "Underlying research files are read-only in this dashboard."
)
