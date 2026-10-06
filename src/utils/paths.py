from pathlib import Path


# src/utils/paths.py
# Project-root-safe paths for the Adaptive Market Risk Intelligence System.

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

RESEARCH_OUTPUT_V1 = DATA_DIR / "research_outputs" / "v1"

DATABASE_DIR = DATA_DIR / "database"

DATABASE_PATH = DATABASE_DIR / "adaptive_market_risk.duckdb"