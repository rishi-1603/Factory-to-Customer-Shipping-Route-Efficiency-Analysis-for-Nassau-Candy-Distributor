"""Data cleaning pipeline: raw Nassau Candy CSV → validated analytical dataset.

Design rules (docs/methodology.md):
- The RAW file is never modified. This pipeline writes data/processed/nassau_clean.csv.
- The timestamp defect is DETECTED, DIAGNOSED, RECOVERED and LOGGED — the raw
  columns are preserved next to the recovered ones so every number is auditable.
- No rows are deleted. Every transformation is logged and reproducible.
"""
from __future__ import annotations

import pandas as pd

from . import config as C


def load_raw(path=None) -> pd.DataFrame:
    """Load the raw CSV exactly as shipped."""
    path = path or C.RAW_CSV
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Clean + enrich. Returns (cleaned_df, transformation_log)."""
    log: list[dict] = []

    def record(step: str, detail: str):
        log.append({"step": step, "detail": detail})

    out = df.copy()
    record("load", f"{len(out):,} rows × {len(out.columns)} columns read")

    # 1. Whitespace strip on text columns (idempotent, non-destructive)
    obj_cols = out.select_dtypes(include="object").columns
    n_strip = int(sum((out[c] != out[c].str.strip()).sum() for c in obj_cols))
    for c in obj_cols:
        out[c] = out[c].str.strip()
    record("whitespace", f"stripped leading/trailing whitespace in {n_strip} cell(s) across text columns")

    # 2. Duplicate check (no deletion without cause)
    n_dupes = int(out.duplicated().sum())
    n_dup_ids = int(out[C.COL_ROW_ID].duplicated().sum())
    record("duplicates", f"{n_dupes} exact duplicate rows, {n_dup_ids} duplicate Row IDs (expected 0; nothing deleted)")

    # 3. Parse dates (DD-MM-YYYY — '30-06-2026' cannot be MM-DD)
    out["order_date_parsed"] = pd.to_datetime(out[C.COL_ORDER_DATE], dayfirst=C.DATE_DAYFIRST)
    out["ship_date_parsed"] = pd.to_datetime(out[C.COL_SHIP_DATE], dayfirst=C.DATE_DAYFIRST)
    n_bad_dates = int(out["order_date_parsed"].isna().sum() + out["ship_date_parsed"].isna().sum())
    assert n_bad_dates == 0, f"unparseable dates: {n_bad_dates}"
    record(
        "date_parsing",
        f"Order Date and Ship Date parsed as DD-MM-YYYY (0 failures). "
        f"Order range {out['order_date_parsed'].min():%Y-%m-%d} → {out['order_date_parsed'].max():%Y-%m-%d}; "
        f"Ship range {out['ship_date_parsed'].min():%Y-%m-%d} → {out['ship_date_parsed'].max():%Y-%m-%d}",
    )

    # 4. THE TIMESTAMP DEFECT — detect, diagnose, recover (never silently fix)
    gap = (out["ship_date_parsed"] - out["order_date_parsed"]).dt.days
    out[C.COL_LEAD_RAW] = gap
    n_impossible = int((gap > 365).sum())
    assert n_impossible == len(out), (
        f"defect model broken: {len(out) - n_impossible} rows have plausible raw gaps"
    )
    n_unique_gaps = int(gap.nunique())
    assert C.RAW_GAP_MIN <= int(gap.min()) and int(gap.max()) <= C.RAW_GAP_MAX, (
        f"raw gap outside the diagnosed bands: {gap.min()}..{gap.max()}"
    )
    out[C.COL_DEFECT_YEARS] = (gap - C.DEFECT_BASE_DAYS) // C.DEFECT_BLOCK_DAYS
    out[C.COL_LEAD] = (gap - C.DEFECT_BASE_DAYS) % C.DEFECT_BLOCK_DAYS
    record(
        "defect_detection",
        f"ALL {len(out):,} ship dates are {C.RAW_GAP_MIN}-{C.RAW_GAP_MAX} days after order dates "
        f"({n_unique_gaps} unique gaps in 3 bands exactly 365 days apart) — a systematic "
        f"multi-year generation offset, not real lead times",
    )
    record(
        "defect_recovery",
        f"recovered true lead = (gap − {C.DEFECT_BASE_DAYS}) mod {C.DEFECT_BLOCK_DAYS}; "
        f"year-blocks stripped: K=0: {(out[C.COL_DEFECT_YEARS] == 0).sum():,}, "
        f"K=1: {(out[C.COL_DEFECT_YEARS] == 1).sum():,}, "
        f"K=2: {(out[C.COL_DEFECT_YEARS] == 2).sum():,}; raw columns preserved for audit",
    )

    # 5. VALIDATION GATE: recovered leads must respect ship-mode semantics.
    medians = out.groupby(C.COL_SHIP_MODE)[C.COL_LEAD].median()
    order = medians.reindex(C.EXPECTED_MODE_MEDIAN_ORDER)
    assert (order.diff().dropna() >= 0).all(), (
        f"recovered leads violate ship-mode ordering: {medians.to_dict()}"
    )
    assert int(out.loc[out[C.COL_SHIP_MODE] == "Same Day", C.COL_LEAD].max()) <= 2, (
        "Same Day shipments with recovered lead > 2 days — recovery unsound"
    )
    record(
        "recovery_validation",
        f"recovered leads respect ship-mode semantics — medians: "
        + ", ".join(f"{m} {v:.0f}d" for m, v in medians.items())
        + "; Same Day max "
        f"{int(out.loc[out[C.COL_SHIP_MODE] == 'Same Day', C.COL_LEAD].max())}d",
    )

    # 6. Factory derivation (Product Name → Factory, per the spec correlation table)
    unmapped = set(out[C.COL_PRODUCT_NAME]) - set(C.FACTORY_MAP)
    assert not unmapped, f"products without a factory mapping: {unmapped}"
    out[C.COL_FACTORY] = out[C.COL_PRODUCT_NAME].map(C.FACTORY_MAP)
    record(
        "factory_mapping",
        f"Factory derived from Product Name via the spec's correlation table "
        f"({out[C.COL_FACTORY].nunique()} factories); raw Product columns preserved",
    )

    # 7. Route definition: Factory → Customer State/Province (per the spec)
    out[C.COL_ROUTE] = out[C.COL_FACTORY] + " → " + out[C.COL_STATE]
    record(
        "route_definition",
        f"route = Factory → Customer State/Province; {out[C.COL_ROUTE].nunique()} unique routes "
        f"across {out[C.COL_FACTORY].nunique()} factories and {out[C.COL_STATE].nunique()} "
        f"state/province codes",
    )

    # 8. Financial identity check: Gross Profit == Sales − Cost
    identity_err = (out[C.COL_SALES] - out[C.COL_COST] - out[C.COL_GROSS_PROFIT]).abs().max()
    assert identity_err < 1e-6, f"Gross Profit != Sales - Cost (max err {identity_err})"
    neg = int((out[C.COL_SALES] <= 0).sum())
    assert neg == 0, f"non-positive sales rows: {neg}"
    record(
        "financial_validation",
        f"Gross Profit == Sales − Cost for all rows (max deviation {identity_err:.1e}); "
        f"0 non-positive sales; total sales ${out[C.COL_SALES].sum():,.2f}",
    )

    # 9. Geographic scope note (spec targets US; Canada rows exist and are kept)
    n_ca = int((out[C.COL_COUNTRY] == "Canada").sum())
    record(
        "geographic_scope",
        f"countries: {', '.join(sorted(out[C.COL_COUNTRY].unique()))} — {n_ca:,} Canadian rows kept "
        f"and filterable (the spec's heatmap covers US states; Canadian provinces appear in "
        f"tables and route analytics)",
    )

    # 10. Missing values: documented, not imputed
    missing = out.isna().sum()
    missing = missing[missing > 0]
    record(
        "missing_values",
        "none — 0 missing cells across all columns"
        if missing.empty
        else "left as-is: " + ", ".join(f"{c} ({v})" for c, v in missing.items()),
    )

    return out, log


def build_processed(write: bool = True) -> tuple[pd.DataFrame, list[dict]]:
    """End-to-end: load raw → clean → (optionally) write processed CSV."""
    df, log = clean(load_raw())
    if write:
        C.PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(C.PROCESSED_CSV, index=False)
        log.append({"step": "write", "detail": f"processed dataset written to {C.PROCESSED_CSV.name}"})
    return df, log
