from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
NIFTY_PATH = DATA_DIR / "processed" / "nifty50_clean.csv"
VIX_PATH = DATA_DIR / "processed" / "india_vix_clean_daily_2018-01-01_2026-09-22.csv"
FORECAST_PATH = DATA_DIR / "research_outputs" / "v1" / "oos_forecasts.csv"
PERFORMANCE_PATH = DATA_DIR / "research_outputs" / "v1" / "model_performance.csv"

def read_csv(path, required, parse_dates=None):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    df = pd.read_csv(path, parse_dates=parse_dates or [])
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")
    return df

@st.cache_data(show_spinner=False)
def load_nifty():
    df = read_csv(NIFTY_PATH, {"Date","Open","High","Low","Close","Volume"}, ["Date"])
    return df.sort_values("Date").drop_duplicates("Date").reset_index(drop=True)

@st.cache_data(show_spinner=False)
def load_vix():
    df = read_csv(VIX_PATH, {"Date","India_VIX"}, ["Date"])
    return df.sort_values("Date").drop_duplicates("Date").reset_index(drop=True)

@st.cache_data(show_spinner=False)
def load_forecasts():
    df = read_csv(FORECAST_PATH, {"Date","Actual_Volatility"}, ["Date"])
    return df.sort_values("Date").reset_index(drop=True)

@st.cache_data(show_spinner=False)
def load_model_performance():
    return read_csv(PERFORMANCE_PATH, {"Model","MAE","RMSE","N","OOS_Start","OOS_End"})
