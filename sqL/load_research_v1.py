from pathlib import Path
import sys
import json
import math

import duckdb
import pandas as pd


# Make the project root importable when this file is executed directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.paths import (
    RESEARCH_OUTPUT_V1,
    DATABASE_DIR,
    DATABASE_PATH,
)


# ============================================================
# RESEARCH OUTPUT V1 → DUCKDB INGESTION
# Adaptive Market Risk Intelligence System
# ============================================================

EXPECTED_MODELS = [
    "Historical_20D",
    "EWMA",
    "GARCH_t",
    "GJR_GARCH_t",
    "EGARCH_t",
    "Historical_20D_VIX",
    "EWMA_VIX",
    "EGARCH_t_VIX",
]

EXPECTED_FORECAST_COLUMNS = [
    "Date",
    "NIFTY_Log_Return",
    "Actual_Volatility",
    "India_VIX_PreReturn",
    "Historical_20D",
    "EWMA",
    "GARCH_t",
    "GJR_GARCH_t",
    "EGARCH_t",
    "Historical_20D_VIX",
    "EWMA_VIX",
    "EGARCH_t_VIX",
]

EXPECTED_PERFORMANCE_COLUMNS = [
    "Model",
    "MAE",
    "RMSE",
    "N",
    "OOS_Start",
    "OOS_End",
]

EXPECTED_OBSERVATIONS = 673
EXPECTED_MODELS_COUNT = 8
EXPECTED_RESEARCH_VERSION = "v1"
EXPECTED_ASSET = "NIFTY 50"
EXPECTED_FORECAST_TARGET = "Next-day volatility"


def fail(message: str) -> None:
    """Stop execution with a clear validation error."""
    raise RuntimeError(f"VALIDATION FAILED: {message}")


def check(condition: bool, message: str) -> None:
    """Raise a validation error when a condition is false."""
    if not condition:
        fail(message)


def main() -> None:

    print("=" * 72)
    print("RESEARCH OUTPUT V1 → DUCKDB INGESTION")
    print("=" * 72)

    # --------------------------------------------------------
    # 1. SOURCE PATHS
    # --------------------------------------------------------

    forecasts_path = RESEARCH_OUTPUT_V1 / "oos_forecasts.csv"
    performance_path = RESEARCH_OUTPUT_V1 / "model_performance.csv"
    manifest_path = RESEARCH_OUTPUT_V1 / "output_manifest.json"
    metadata_path = RESEARCH_OUTPUT_V1 / "research_metadata.json"

    print("\n[1] Checking source files...")

    for path in [
        forecasts_path,
        performance_path,
        manifest_path,
        metadata_path,
    ]:
        check(path.exists(), f"Missing source file: {path}")

    print("PASS: All required v1 source files exist.")

    # --------------------------------------------------------
    # 2. LOAD SOURCE FILES
    # --------------------------------------------------------

    print("\n[2] Loading authoritative v1 outputs...")

    forecasts = pd.read_csv(forecasts_path)
    performance = pd.read_csv(performance_path)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    print(f"Forecast rows: {len(forecasts)}")
    print(f"Performance rows: {len(performance)}")

    # --------------------------------------------------------
    # 3. VALIDATE METADATA CONTRACT
    # --------------------------------------------------------

    print("\n[3] Validating research metadata...")

    check(
        metadata.get("research_version") == EXPECTED_RESEARCH_VERSION,
        "research_version is not v1.",
    )

    check(
        metadata.get("asset") == EXPECTED_ASSET,
        "Unexpected research asset.",
    )

    check(
        metadata.get("forecast_target") == EXPECTED_FORECAST_TARGET,
        "Unexpected forecast target.",
    )

    check(
        metadata.get("observations") == EXPECTED_OBSERVATIONS,
        "Metadata observation count does not equal 673.",
    )

    check(
        metadata.get("information_set")
        == "Strict pre-return information set",
        "Information-set definition does not match frozen v1 metadata.",
    )

    validation = metadata.get("validation", {})

    check(
        validation.get("missing_values") == 0,
        "Frozen metadata does not report zero missing values.",
    )

    check(
        validation.get("duplicate_dates") == 0,
        "Frozen metadata does not report zero duplicate dates.",
    )

    check(
        validation.get("non_finite_values") == 0,
        "Frozen metadata does not report zero non-finite values.",
    )

    check(
        validation.get("chronological_order") is True,
        "Frozen metadata does not report chronological ordering.",
    )

    check(
        validation.get("data_contract") == "PASSED",
        "Frozen metadata data contract is not PASSED.",
    )

    print("PASS: Research metadata contract validated.")

    # --------------------------------------------------------
    # 4. VALIDATE MANIFEST
    # --------------------------------------------------------

    print("\n[4] Validating output manifest...")

    check(
        manifest.get("research_version") == EXPECTED_RESEARCH_VERSION,
        "Manifest research_version does not equal v1.",
    )

    required_manifest_files = [
        "oos_forecasts.csv",
        "model_performance.csv",
        "research_metadata.json",
    ]

    for filename in required_manifest_files:
        check(
            filename in manifest,
            f"Manifest is missing entry for {filename}.",
        )

    print("PASS: Output manifest validated.")

    # --------------------------------------------------------
    # 5. VALIDATE FORECAST SCHEMA
    # --------------------------------------------------------

    print("\n[5] Validating OOS forecast schema...")

    check(
        forecasts.columns.tolist() == EXPECTED_FORECAST_COLUMNS,
        "OOS forecast columns do not exactly match frozen v1 schema.",
    )

    check(
        len(forecasts) == EXPECTED_OBSERVATIONS,
        "OOS forecast row count does not equal 673.",
    )

    check(
        forecasts["Date"].is_unique,
        "OOS forecast dates are not unique.",
    )

    dates = pd.to_datetime(forecasts["Date"], errors="coerce")

    check(
        dates.notna().all(),
        "One or more OOS dates cannot be parsed.",
    )

    check(
        dates.is_monotonic_increasing,
        "OOS forecast dates are not chronological.",
    )

    numeric_forecast_columns = [
        c for c in EXPECTED_FORECAST_COLUMNS if c != "Date"
    ]

    check(
        not forecasts[numeric_forecast_columns].isna().any().any(),
        "OOS forecast table contains missing numeric values.",
    )

    check(
        forecasts[numeric_forecast_columns]
        .map(math.isfinite)
        .all()
        .all(),
        "OOS forecast table contains non-finite numeric values.",
    )
    print("PASS: OOS forecast schema and integrity validated.")

    # --------------------------------------------------------
    # 6. VALIDATE PERFORMANCE SCHEMA
    # --------------------------------------------------------

    print("\n[6] Validating model-performance schema...")

    check(
        performance.columns.tolist() == EXPECTED_PERFORMANCE_COLUMNS,
        "Model-performance columns do not exactly match frozen v1 schema.",
    )

    check(
        len(performance) == EXPECTED_MODELS_COUNT,
        "Model-performance row count does not equal 8.",
    )

    check(
        performance["Model"].tolist() == EXPECTED_MODELS,
        "Model list does not exactly match frozen v1 model order.",
    )

    check(
        performance["Model"].is_unique,
        "Model-performance table contains duplicate models.",
    )

    numeric_performance_columns = [
        "MAE",
        "RMSE",
        "N",
    ]

    check(
        not performance[numeric_performance_columns].isna().any().any(),
        "Model-performance table contains missing values.",
    )

    check(
        performance["N"].eq(EXPECTED_OBSERVATIONS).all(),
        "Model-performance N does not equal 673 for every model.",
    )

    print("PASS: Model-performance schema and integrity validated.")

    # --------------------------------------------------------
    # 7. CREATE DATABASE DIRECTORY
    # --------------------------------------------------------

    print("\n[7] Preparing DuckDB database...")

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # 8. CONNECT TO DUCKDB
    # --------------------------------------------------------

    print(f"Database: {DATABASE_PATH}")

    con = duckdb.connect(str(DATABASE_PATH))

    try:

        # ----------------------------------------------------
        # 9. CREATE RESEARCH TABLES
        # ----------------------------------------------------

        print("\n[8] Creating research tables...")

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS research_oos_forecasts (
                Date DATE,
                NIFTY_Log_Return DOUBLE,
                Actual_Volatility DOUBLE,
                India_VIX_PreReturn DOUBLE,
                Historical_20D DOUBLE,
                EWMA DOUBLE,
                GARCH_t DOUBLE,
                GJR_GARCH_t DOUBLE,
                EGARCH_t DOUBLE,
                Historical_20D_VIX DOUBLE,
                EWMA_VIX DOUBLE,
                EGARCH_t_VIX DOUBLE,
                research_version VARCHAR,
                asset VARCHAR,
                forecast_target VARCHAR,
                PRIMARY KEY (Date, research_version)
            )
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS research_model_performance (
                Model VARCHAR,
                MAE DOUBLE,
                RMSE DOUBLE,
                N INTEGER,
                OOS_Start DATE,
                OOS_End DATE,
                research_version VARCHAR,
                asset VARCHAR,
                forecast_target VARCHAR,
                PRIMARY KEY (Model, research_version)
            )
            """
        )

        # ----------------------------------------------------
        # 10. LOAD V1 SAFELY
        # ----------------------------------------------------

        print("\n[9] Loading frozen v1 data...")

        # Prepare copies so source DataFrames remain unchanged.
        forecast_load = forecasts.copy()
        performance_load = performance.copy()

        forecast_load["Date"] = pd.to_datetime(
            forecast_load["Date"]
        ).dt.date

        forecast_load["research_version"] = EXPECTED_RESEARCH_VERSION
        forecast_load["asset"] = EXPECTED_ASSET
        forecast_load["forecast_target"] = EXPECTED_FORECAST_TARGET

        performance_load["OOS_Start"] = pd.to_datetime(
            performance_load["OOS_Start"]
        ).dt.date

        performance_load["OOS_End"] = pd.to_datetime(
            performance_load["OOS_End"]
        ).dt.date

        performance_load["research_version"] = EXPECTED_RESEARCH_VERSION
        performance_load["asset"] = EXPECTED_ASSET
        performance_load["forecast_target"] = EXPECTED_FORECAST_TARGET


        # ----------------------------------------------------
        # 10A. CHECK WHETHER THIS VERSION ALREADY EXISTS
        # ----------------------------------------------------

        existing_forecast_count = con.execute(
            """
            SELECT COUNT(*)
            FROM research_oos_forecasts
            WHERE research_version = ?
            """,
            [EXPECTED_RESEARCH_VERSION],
        ).fetchone()[0]

        existing_performance_count = con.execute(
            """
            SELECT COUNT(*)
            FROM research_model_performance
            WHERE research_version = ?
            """,
            [EXPECTED_RESEARCH_VERSION],
        ).fetchone()[0]


        # ----------------------------------------------------
        # 10B. LOAD ONLY IF VERSION IS NOT PRESENT
        # ----------------------------------------------------

        if existing_forecast_count == 0 and existing_performance_count == 0:

            print(
                f"No existing {EXPECTED_RESEARCH_VERSION} data found. "
                "Loading authoritative source outputs..."
            )

            con.register("forecast_load_df", forecast_load)
            con.register("performance_load_df", performance_load)

            con.execute(
                """
                INSERT INTO research_oos_forecasts
                SELECT
                    Date,
                    NIFTY_Log_Return,
                    Actual_Volatility,
                    India_VIX_PreReturn,
                    Historical_20D,
                    EWMA,
                    GARCH_t,
                    GJR_GARCH_t,
                    EGARCH_t,
                    Historical_20D_VIX,
                    EWMA_VIX,
                    EGARCH_t_VIX,
                    research_version,
                    asset,
                    forecast_target
                FROM forecast_load_df
                """
            )

            con.execute(
                """
                INSERT INTO research_model_performance
                SELECT
                    Model,
                    MAE,
                    RMSE,
                    N,
                    OOS_Start,
                    OOS_End,
                    research_version,
                    asset,
                    forecast_target
                FROM performance_load_df
                """
            )

            print(
                f"PASS: {EXPECTED_RESEARCH_VERSION} loaded successfully."
            )

        elif (
            existing_forecast_count == EXPECTED_OBSERVATIONS
            and existing_performance_count == EXPECTED_MODELS_COUNT
        ):

            print(
                f"{EXPECTED_RESEARCH_VERSION} already exists in the database. "
                "No reload performed."
            )
            print(
                "Existing data will be validated against the authoritative "
                "source outputs."
            )

        else:

            fail(
                f"Partial {EXPECTED_RESEARCH_VERSION} data already exists: "
                f"{existing_forecast_count} forecast rows and "
                f"{existing_performance_count} performance rows. "
                "Refusing to modify the database."
            )
        # ----------------------------------------------------
        # 11. DATABASE INTEGRITY CHECKS
        # ----------------------------------------------------

        print("\n[10] Validating loaded database...")

        forecast_count = con.execute(
            "SELECT COUNT(*) FROM research_oos_forecasts"
        ).fetchone()[0]

        performance_count = con.execute(
            "SELECT COUNT(*) FROM research_model_performance"
        ).fetchone()[0]

        check(
            forecast_count == EXPECTED_OBSERVATIONS,
            f"Database forecast row count is {forecast_count}, expected 673.",
        )

        check(
            performance_count == EXPECTED_MODELS_COUNT,
            f"Database model row count is {performance_count}, expected 8.",
        )

        db_missing = con.execute(
            """
            SELECT COUNT(*)
            FROM research_oos_forecasts
            WHERE
                NIFTY_Log_Return IS NULL
                OR Actual_Volatility IS NULL
                OR India_VIX_PreReturn IS NULL
                OR Historical_20D IS NULL
                OR EWMA IS NULL
                OR GARCH_t IS NULL
                OR GJR_GARCH_t IS NULL
                OR EGARCH_t IS NULL
                OR Historical_20D_VIX IS NULL
                OR EWMA_VIX IS NULL
                OR EGARCH_t_VIX IS NULL
            """
        ).fetchone()[0]


        check(
            db_missing == 0,
            f"Database contains {db_missing} rows with missing forecast values.",
        )

        db_versions = con.execute(
            """
            SELECT DISTINCT research_version
            FROM research_oos_forecasts
            ORDER BY research_version
            """
        ).fetchall()

        check(
            (EXPECTED_RESEARCH_VERSION,) in db_versions,
            f"Expected research version {EXPECTED_RESEARCH_VERSION} "
            f"was not found in the database. Found: {db_versions}",
        )

        print(f"Research versions present: {db_versions}")

        # ----------------------------------------------------
        # 12. SOURCE-TO-DATABASE VALUE CHECK
        # ----------------------------------------------------

        print("\n[11] Performing source-to-database reconciliation...")

        source_first = forecasts.iloc[0]
        source_last = forecasts.iloc[-1]

        db_first = con.execute(
            """
            SELECT
                Date,
                NIFTY_Log_Return,
                Actual_Volatility,
                India_VIX_PreReturn,
                EGARCH_t_VIX
            FROM research_oos_forecasts
            ORDER BY Date
            LIMIT 1
            """
        ).fetchone()

        db_last = con.execute(
            """
            SELECT
                Date,
                NIFTY_Log_Return,
                Actual_Volatility,
                India_VIX_PreReturn,
                EGARCH_t_VIX
            FROM research_oos_forecasts
            ORDER BY Date DESC
            LIMIT 1
            """
        ).fetchone()

        check(
            str(db_first[0]) == str(pd.to_datetime(source_first["Date"]).date()),
            "First date reconciliation failed.",
        )

        check(
            abs(db_first[1] - source_first["NIFTY_Log_Return"]) < 1e-12,
            "First NIFTY return reconciliation failed.",
        )

        check(
            abs(db_first[2] - source_first["Actual_Volatility"]) < 1e-12,
            "First actual-volatility reconciliation failed.",
        )

        check(
            abs(db_first[4] - source_first["EGARCH_t_VIX"]) < 1e-12,
            "First EGARCH_t_VIX reconciliation failed.",
        )

        check(
            str(db_last[0]) == str(pd.to_datetime(source_last["Date"]).date()),
            "Last date reconciliation failed.",
        )

        check(
            abs(db_last[1] - source_last["NIFTY_Log_Return"]) < 1e-12,
            "Last NIFTY return reconciliation failed.",
        )

        check(
            abs(db_last[2] - source_last["Actual_Volatility"]) < 1e-12,
            "Last actual-volatility reconciliation failed.",
        )

        check(
            abs(db_last[4] - source_last["EGARCH_t_VIX"]) < 1e-12,
            "Last EGARCH_t_VIX reconciliation failed.",
        )

        print("PASS: Source and database values reconcile.")

        # ----------------------------------------------------
        # 13. FINAL DATABASE SUMMARY
        # ----------------------------------------------------

        print("\n[12] Database summary")

        summary = con.execute(
            """
            SELECT
                MIN(Date) AS OOS_Start,
                MAX(Date) AS OOS_End,
                COUNT(*) AS Observations,
                COUNT(DISTINCT research_version) AS Research_Versions
            FROM research_oos_forecasts
            """
        ).fetchone()

        print(f"OOS Start:          {summary[0]}")
        print(f"OOS End:            {summary[1]}")
        print(f"Observations:       {summary[2]}")
        print(f"Research versions:  {summary[3]}")

        print("\n" + "=" * 72)
        print("INGESTION STATUS: PASS")
        print("=" * 72)
        print(f"Database created/updated: {DATABASE_PATH}")

    finally:
        con.close()


if __name__ == "__main__":
    main()
