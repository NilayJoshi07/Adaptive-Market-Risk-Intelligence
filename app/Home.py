import streamlit as st
from app.data_access import load_nifty, load_vix, load_forecasts, load_model_performance

st.set_page_config(page_title="Adaptive Market Risk Intelligence", page_icon="📈", layout="wide")
st.title("Adaptive Market Risk Intelligence System")
st.subheader("Market context • Out-of-sample forecasts • Risk decision support")
st.write("An interactive presentation layer over existing market data and frozen research outputs. It does not retrain models, modify research files, or execute trades.")
st.info("Data are read from local project files. Dates below are latest available observations, not live market quotes.")

try:
    nifty, vix = load_nifty(), load_vix()
    forecasts, performance = load_forecasts(), load_model_performance()
    a,b,c,d = st.columns(4)
    a.metric("NIFTY observations", f"{len(nifty):,}")
    b.metric("Latest NIFTY date", nifty.Date.max().strftime("%d %b %Y"))
    c.metric("Latest India VIX date", vix.Date.max().strftime("%d %b %Y"))
    d.metric("OOS forecast observations", f"{len(forecasts):,}")
    st.markdown("### Available research outputs")
    st.write(f"Forecast models in performance file: {len(performance)}")
    st.write(f"Forecast evaluation window: {forecasts.Date.min():%d %b %Y} to {forecasts.Date.max():%d %b %Y}")
    st.write(
    "Navigate using the sidebar to explore Market Overview, "
    "Forecast Lab, Rolling Historical Risk Monitor, and "
    "Decision Support & Scenario Lab."
    )
except (FileNotFoundError, ValueError, KeyError) as exc:
    st.error(f"Unable to load a required project dataset: {exc}")

st.caption("Historical research interface only. Historical performance does not guarantee future results; this application is not approved for live trading.")
