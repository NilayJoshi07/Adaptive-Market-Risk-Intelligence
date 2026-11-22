from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="ML Experiments | AMRIS",
    page_icon="🧪",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = PROJECT_ROOT / "data" / "ml_experiments" / "v1"

FILES = {
    "initial": EXPERIMENT_DIR / "initial_model_comparison.csv",
    "walk_forward": EXPERIMENT_DIR / "walk_forward_model_comparison.csv",
    "mixtures": EXPERIMENT_DIR / "mix_strategy_comparison.csv",
    "formal_tests": EXPERIMENT_DIR / "formal_ml_vs_egarch_comparison.csv",
    "vix_value": EXPERIMENT_DIR / "vix_incremental_value_analysis.csv",
    "regimes": EXPERIMENT_DIR / "rf_vs_egarch_vix_regime_analysis.csv",
    "rf_error_counts": EXPERIMENT_DIR / "rf_vs_egarch_vix_error_comparison.csv",
    "initial_predictions": EXPERIMENT_DIR / "initial_model_predictions.csv",
    "walk_forward_predictions": EXPERIMENT_DIR / "walk_forward_predictions.csv",
    "mixture_predictions": EXPERIMENT_DIR / "mix_strategy_predictions.csv",
}


def read_csv_checked(path: Path, required_columns: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required experiment artifact not found: {path}")
    df = pd.read_csv(path)
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")
    if df.empty:
        raise ValueError(f"{path.name} is empty")
    return df


@st.cache_data(show_spinner=False)
def load_artifact(path_string: str, modified_time: float, required_columns: tuple[str, ...]) -> pd.DataFrame:
    del modified_time  # cache key changes when the file's modification time changes
    path = Path(path_string)
    return read_csv_checked(path, set(required_columns))


def load_optional(key: str, required_columns: set[str]):
    path = FILES[key]
    if not path.exists():
        return None, f"Not found: {path.name}"
    try:
        df = load_artifact(str(path), path.stat().st_mtime, tuple(sorted(required_columns)))
        return df, None
    except (ValueError, FileNotFoundError, pd.errors.ParserError) as exc:
        return None, str(exc)


def pct(value):
    return "N/A" if pd.isna(value) else f"{value:.4%}"


def clean_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["MAE", "RMSE"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["N"] = pd.to_numeric(out["N"], errors="coerce")
    if out[["MAE", "RMSE", "N"]].isna().any().any():
        raise ValueError("Model comparison contains missing or invalid MAE/RMSE/N values.")
    if not np.isfinite(out[["MAE", "RMSE", "N"]].to_numpy(dtype=float)).all():
        raise ValueError("Model comparison contains non-finite numeric values.")
    return out.sort_values("MAE").reset_index(drop=True)


st.title("ML Volatility Experiments")
st.caption("AMRIS | Experimental model comparisons and saved evidence")
st.info(
    "This page reads saved experiment artifacts only. It does not retrain models, "
    "overwrite frozen research outputs, or promote experimental models into the "
    "business-decision pipeline."
)

st.markdown(
    "The experiment target is the project’s absolute one-day log-return proxy "
    "(`Actual_Abs_Return` / `Actual_Volatility`). MAE and RMSE therefore describe "
    "forecast errors against that target; they should not be interpreted as direct "
    "measurements of latent volatility."
)

# Required comparison artifacts. Other diagnostic artifacts are optional and
# displayed with explicit warnings when absent.
required_specs = {
    "initial": {"Model", "MAE", "RMSE", "N"},
    "walk_forward": {"Model", "MAE", "RMSE", "N"},
    "mixtures": {"Model", "MAE", "RMSE", "N"},
}
loaded = {}
errors = {}
for key, cols in required_specs.items():
    loaded[key], errors[key] = load_optional(key, cols)

for key, err in errors.items():
    if err:
        st.error(f"Cannot display {key.replace('_', ' ')} comparison: {err}")

if any(loaded[key] is None for key in required_specs):
    st.stop()

try:
    initial = clean_metrics(loaded["initial"])
    walk_forward = clean_metrics(loaded["walk_forward"])
    mixtures = clean_metrics(loaded["mixtures"])
except ValueError as exc:
    st.error(str(exc))
    st.stop()

# Consolidated overview, preserving source-specific experiment labels.
all_results = pd.concat(
    [
        initial.assign(Experiment="Initial ML"),
        walk_forward.assign(Experiment="Walk-forward"),
        mixtures.assign(Experiment="Forecast mixtures"),
    ],
    ignore_index=True,
)

benchmark_rows = all_results.loc[all_results["Model"].eq("EGARCH_t_VIX")]
if benchmark_rows.empty:
    st.warning("EGARCH_t_VIX was not found in every comparison artifact; check the source files before comparing experiments.")

best_row = all_results.sort_values("MAE").iloc[0]
model_count = all_results["Model"].nunique()
observation_counts = sorted(all_results["N"].dropna().astype(int).unique())

m1, m2, m3 = st.columns(3)
m1.metric("Comparison artifacts", "3")
m2.metric("Distinct model / strategy labels", f"{model_count}")
m3.metric("Lowest saved MAE", f"{best_row['MAE']:.6f}", help=f"{best_row['Model']} · {best_row['Experiment']}")
st.caption("Observation counts recorded in the comparison files: " + ", ".join(f"{n:,}" for n in observation_counts))

st.divider()
st.header("1. Model and strategy performance")
experiment_choice = st.selectbox(
    "Select saved comparison",
    options=["Initial ML", "Walk-forward", "Forecast mixtures", "Combined overview"],
    index=0,
)

if experiment_choice == "Initial ML":
    shown = initial.assign(Experiment="Initial ML")
elif experiment_choice == "Walk-forward":
    shown = walk_forward.assign(Experiment="Walk-forward")
elif experiment_choice == "Forecast mixtures":
    shown = mixtures.assign(Experiment="Forecast mixtures")
else:
    shown = all_results.sort_values("MAE").reset_index(drop=True)

st.caption("Lower MAE/RMSE indicates smaller errors for the stated target and evaluation sample.")
st.dataframe(
    shown[[c for c in ["Experiment", "Model", "Type", "MAE", "RMSE", "N"] if c in shown.columns]].style.format({"MAE": "{:.6f}", "RMSE": "{:.6f}"}),
    use_container_width=True,
    hide_index=True,
)

metric_choice = st.radio("Chart metric", ["MAE", "RMSE"], horizontal=True, key="ml_metric_choice")
chart_data = shown.sort_values(metric_choice)
fig = px.bar(
    chart_data,
    x="Model",
    y=metric_choice,
    color="Experiment" if "Experiment" in chart_data.columns else None,
    title=f"Saved {metric_choice} comparison",
    labels={metric_choice: metric_choice, "Model": "Model / strategy"},
)
fig.update_layout(xaxis_tickangle=-35)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.header("2. Walk-forward retraining")
st.write(
    "Compare fixed-model and monthly expanding-window results using the saved "
    "walk-forward comparison. The reported sample contains 673 out-of-sample observations."
)
st.dataframe(walk_forward.sort_values("MAE"), use_container_width=True, hide_index=True)

st.divider()
st.header("3. Forecast mixture experiments")
st.write(
    "The mixtures combine existing statistical forecasts. In the supplied results, "
    "none of the saved mixtures beats EGARCH-t + VIX on MAE."
)
st.dataframe(mixtures.sort_values("MAE"), use_container_width=True, hide_index=True)

st.divider()
st.header("4. Statistical comparison evidence")
formal, formal_err = load_optional(
    "formal_tests",
    {"ML_Model", "Loss", "Mean_Loss_Difference_ML_minus_EGARCH", "Test_Statistic", "P_Value", "HAC_Max_Lag", "N"},
)
if formal is None:
    st.warning(f"Formal comparison table unavailable: {formal_err}")
else:
    for col in ["Mean_Loss_Difference_ML_minus_EGARCH", "Test_Statistic", "P_Value", "HAC_Max_Lag", "N"]:
        formal[col] = pd.to_numeric(formal[col], errors="coerce")
    st.caption(
        "The supplied formal-test file compares the listed ML models with EGARCH-t + VIX. "
        "Positive ML-minus-benchmark loss differences indicate higher loss for the ML model. "
        "Check the Loss definition and p-value before interpreting each row."
    )
    st.dataframe(formal, use_container_width=True, hide_index=True)

vix, vix_err = load_optional(
    "vix_value",
    {"Baseline", "Challenger", "Baseline_MAE", "Challenger_MAE", "MAE_Improvement", "Baseline_RMSE", "Challenger_RMSE", "RMSE_Improvement", "HAC_p_Absolute_Loss", "HAC_p_Squared_Loss", "N"},
)
if vix is None:
    st.warning(f"VIX incremental-value table unavailable: {vix_err}")
else:
    st.subheader("Incremental value of India VIX")
    st.caption("These rows compare the saved statistical baseline with its VIX-enhanced challenger.")
    st.dataframe(vix, use_container_width=True, hide_index=True)

st.divider()
st.header("5. Random Forest diagnostic evidence")
regimes, regime_err = load_optional("regimes", {"Regime", "Model", "N", "MAE", "RMSE"})
if regimes is None:
    st.warning(f"Regime analysis unavailable: {regime_err}")
else:
    st.subheader("Error by descriptive regime")
    st.dataframe(regimes, use_container_width=True, hide_index=True)

counts, counts_err = load_optional(
    "rf_error_counts",
    {"Evaluation_Observations", "RF_Better_Absolute_Error_Count", "EGARCH_Better_Absolute_Error_Count", "Tied_Absolute_Error_Count", "Mean_RF_Minus_EGARCH_Absolute_Error"},
)
if counts is None:
    st.warning(f"Paired error-count summary unavailable: {counts_err}")
else:
    row = counts.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("RF lower absolute error", f"{int(row['RF_Better_Absolute_Error_Count']):,}")
    c2.metric("EGARCH-t + VIX lower error", f"{int(row['EGARCH_Better_Absolute_Error_Count']):,}")
    c3.metric("Ties", f"{int(row['Tied_Absolute_Error_Count']):,}")
    st.caption(f"Mean RF minus EGARCH-t + VIX absolute error: {row['Mean_RF_Minus_EGARCH_Absolute_Error']:.6f}.")

st.divider()
st.header("6. Ridge stacking status")
st.warning(
    "Ridge stacking results are documented in the Notebook 04 work log, but a standalone "
    "Ridge prediction/comparison artifact was not present in the supplied experiment ZIP. "
    "This page therefore does not insert the reported Ridge metrics into the saved CSV "
    "leaderboard or treat Ridge as a validated production forecast. Save and validate a "
    "dedicated Ridge results artifact before adding it to this comparison."
)

st.header("Interpretation and safeguards")
st.markdown(
    """
    - These are experimental results, not automatic replacements for the established forecast pipeline.
    - Compare models on the same target, dates, and sample size; inspect the saved sample count.
    - A lower observed MAE/RMSE does not by itself establish statistical superiority.
    - Statistical tests are interpreted using their stated loss differential and p-value.
    - The page reads artifacts under `data/ml_experiments/v1/` and does not write to research outputs.
    """
)
st.caption("Source: saved CSV artifacts under data/ml_experiments/v1/. No model is retrained by this page.")