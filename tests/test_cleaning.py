"""Cleaning pipeline tests — reproducibility and data-quality rules."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config as C  # noqa: E402
from src.data_cleaning import clean, load_raw  # noqa: E402


def test_raw_loads_with_expected_shape():
    raw = load_raw()
    assert raw.shape == (10_194, 18)


def test_no_exact_duplicates(df):
    assert df.duplicated().sum() == 0
    assert df[C.COL_ROW_ID].duplicated().sum() == 0


def test_factory_mapping_complete_and_pinned(df):
    # every product mapped; all 5 factories present
    assert set(df[C.COL_FACTORY]) == set(C.FACTORY_MAP.values())
    counts = df[C.COL_FACTORY].value_counts().to_dict()
    assert counts == {
        "Lot's O' Nuts": 5692, "Wicked Choccy's": 4152, "Secret Factory": 217,
        "The Other Factory": 100, "Sugar Shack": 33,
    }


def test_route_count_pinned(df):
    # the spec-level headline: 196 unique Factory → State/Province routes
    assert df[C.COL_ROUTE].nunique() == 196
    assert df[C.COL_STATE].nunique() == 59
    assert df[C.COL_REGION].nunique() == 4


def test_financial_identity_holds(df):
    err = (df[C.COL_SALES] - df[C.COL_COST] - df[C.COL_GROSS_PROFIT]).abs().max()
    assert err < 1e-6
    assert (df[C.COL_SALES] > 0).all()
    assert abs(df[C.COL_SALES].sum() - 141_783.63) < 0.01
    assert abs(df[C.COL_GROSS_PROFIT].sum() - 93_442.80) < 0.01


def test_geographic_scope(df):
    counts = df[C.COL_COUNTRY].value_counts().to_dict()
    assert counts == {"United States": 9994, "Canada": 200}


def test_no_missing_values(df):
    assert int(df.isna().sum().sum()) == 0


def test_cleaning_log_documents_every_step():
    raw = load_raw()
    _, log = clean(raw)
    steps = [e["step"] for e in log]
    for expected in ("load", "whitespace", "duplicates", "date_parsing",
                     "defect_detection", "defect_recovery", "recovery_validation",
                     "factory_mapping", "route_definition", "financial_validation",
                     "geographic_scope", "missing_values"):
        assert expected in steps, expected
