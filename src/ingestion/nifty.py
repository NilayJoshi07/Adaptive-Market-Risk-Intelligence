from pathlib import Path

import pandas as pd
import yfinance as yf


def download_nifty_data(
    start_date: str,
    end_date: str,
    output_path: str = "data/raw/nifty50_yfinance.csv",
) -> pd.DataFrame:

    data = yf.download(
        "^NSEI",
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise ValueError("No NIFTY data was downloaded.")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data.to_csv(output_file)

    return data