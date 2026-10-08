"""The signature tests — the timestamp defect: detection, recovery, validation.

These are the most important tests in the repo: they prove the lead-time KPIs
are built on a diagnosed and validated recovery, not on broken raw dates.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config as C  # noqa: E402
from src.data_cleaning import clean, load_raw  # noqa: E402


def test_defect_present_in_raw_data():
    """Every raw row ships with an impossible multi-year ship-order gap."""
    raw = load_raw()
    od = pd.to_datetime(raw[C.COL_ORDER_DATE], dayfirst=True)
    sd = pd.to_datetime(raw[C.COL_SHIP_DATE], dayfirst=True)
    gap = (sd - od).dt.days
    # the defect affects ALL rows — the headline data-quality catch
    assert (gap > 365).all(), "some rows have plausible raw gaps — defect model changed?"
    assert int(gap.min()) == 904 and int(gap.max()) == 1642


def test_gap_bands_are_exactly_one_block_apart():
    """The raw gaps cluster into 3 bands exactly 365 days apart — the
    generative signature of whole-year offsets, not real lead times."""
    raw = load_raw()
    od = pd.to_datetime(raw[C.COL_ORDER_DATE], dayfirst=True)
    sd = pd.to_datetime(raw[C.COL_SHIP_DATE], dayfirst=True)
    gap = (sd - od).dt.days
    unique = sorted(gap.unique())
    bands = sorted({(g - 904) // 365 for g in unique})
    assert bands == [0, 1, 2], f"unexpected year-block structure: {bands}"
    # every residual after stripping blocks is a plausible 0-11 day lead
    resid = (gap - 904) % 365
    assert int(resid.max()) <= 11
    assert int(resid.min()) >= 0


def test_recovery_distribution_pinned(df):
    """The recovered lead distribution — pinned exactly."""
    dist = df[C.COL_LEAD].value_counts().sort_index().to_dict()
    assert dist == {0: 350, 1: 375, 2: 1089, 3: 1081, 4: 2328,
                    5: 2450, 6: 1476, 7: 824, 8: 219, 11: 2}


def test_recovery_validates_against_ship_mode_semantics(df):
    """THE validation gate: recovered leads must order by ship mode."""
    med = df.groupby(C.COL_SHIP_MODE)[C.COL_LEAD].median()
    assert med["Same Day"] == 0
    assert med["First Class"] == 3
    assert med["Second Class"] == 3
    assert med["Standard Class"] == 5
    # non-overlapping extremes
    assert int(df.loc[df[C.COL_SHIP_MODE] == "Same Day", C.COL_LEAD].max()) <= 2
    assert int(df.loc[df[C.COL_SHIP_MODE] == "Standard Class", C.COL_LEAD].min()) >= 3


def test_year_block_counts_pinned(df):
    assert df[C.COL_DEFECT_YEARS].value_counts().to_dict() == {1: 4764, 2: 3379, 0: 2051}


def test_clean_pipeline_fails_loudly_on_mode_violation():
    """If a future data refresh breaks the mode ordering, clean() must raise —
    never publish unreliable recovered leads."""
    raw = load_raw().head(200).copy()
    # sabotage: force Same Day leads to be huge
    mask = raw[C.COL_SHIP_MODE] == "Same Day"
    raw.loc[mask, C.COL_SHIP_DATE] = (
        pd.to_datetime(raw.loc[mask, C.COL_ORDER_DATE], dayfirst=True)
        + pd.Timedelta(days=904 + 365 + 10)
    ).dt.strftime("%d-%m-%Y")
    with pytest.raises(AssertionError):
        clean(raw)
