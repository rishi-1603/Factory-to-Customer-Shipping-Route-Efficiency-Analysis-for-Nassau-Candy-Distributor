"""Single data-access entry point used by the dashboard and scripts.

Resolution order:
1. ``data/processed/nassau_clean.csv`` — local dev, built by scripts/01_clean_data.py
2. ``data/raw/nassau_candy_shipments.csv`` — the 2 MB source ships in git, so a
   fresh checkout can always clean it in memory (Streamlit Cloud path).
"""
from __future__ import annotations

import pandas as pd

from . import config as C
from .data_cleaning import clean


def get_processed_df() -> pd.DataFrame:
    """Return the cleaned dataset — from disk when present, else clean in memory."""
    if C.PROCESSED_CSV.exists():
        return pd.read_csv(C.PROCESSED_CSV)
    df, _ = clean(pd.read_csv(C.RAW_CSV))
    return df
