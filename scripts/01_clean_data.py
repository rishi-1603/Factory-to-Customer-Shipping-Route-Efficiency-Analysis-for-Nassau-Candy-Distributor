"""01_clean_data.py — raw -> processed + data-quality report.

Run:  python scripts/01_clean_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_cleaning import build_processed  # noqa: E402
from src import config as C  # noqa: E402


def main() -> None:
    df, log = build_processed(write=True)
    C.REPORTS_DIR.mkdir(exist_ok=True)
    lines = [
        "# Data Quality Report",
        "",
        f"Source: `data/raw/{C.RAW_CSV.name}` → Processed: `data/processed/{C.PROCESSED_CSV.name}`",
        "",
        "## Transformation log",
        "",
        "| Step | Detail |",
        "|---|---|",
    ]
    for entry in log:
        lines.append(f"| {entry['step']} | {entry['detail']} |")

    lead = df[C.COL_LEAD]
    lines += [
        "",
        "## Dataset profile",
        "",
        f"- Rows: {len(df):,} (order-line grain; {df[C.COL_ORDER_ID].nunique():,} unique orders)",
        f"- Columns: {len(df.columns)} (18 raw + {len(df.columns) - 18} derived)",
        f"- Factories: {df[C.COL_FACTORY].nunique()} | Products: {df[C.COL_PRODUCT_NAME].nunique()} "
        f"| State/province codes: {df[C.COL_STATE].nunique()} | Regions: {df[C.COL_REGION].nunique()}",
        f"- Unique routes (Factory → State): {df[C.COL_ROUTE].nunique():,}",
        f"- Total sales: ${df[C.COL_SALES].sum():,.2f} | Gross profit: ${df[C.COL_GROSS_PROFIT].sum():,.2f}",
        "",
        "## The timestamp defect (the most important data-quality finding)",
        "",
        f"ALL {len(df):,} ship dates sit {C.RAW_GAP_MIN}-{C.RAW_GAP_MAX} days after their order dates — "
        "an impossible 2.5-4.5 year 'lead time' for candy distribution. The gap decomposes exactly "
        f"into `{C.DEFECT_BASE_DAYS} + 365×K + true_lead` (K ∈ {{0,1,2}}, true lead 0-11 days): a "
        "systematic multi-year generation offset. Recovery strips the offset and is validated "
        "against ship-mode semantics (Same Day median 0 < First Class 3 ≈ Second Class 3 < "
        "Standard 5). Raw columns (`lead_time_raw_days`, both date columns) are preserved so every "
        "recovered number is auditable.",
        "",
        "## Known limitations (documented, not 'fixed')",
        "",
        "1. **Ship dates are defective as shipped** — all lead-time KPIs use the *recovered* lead, "
        "with the defect model, validation and per-row audit trail above.",
        "2. **Order-line grain** — an Order ID can span multiple lines; route volumes count lines, "
        "not orders (documented).",
        "3. **US + Canada** — the spec targets US distribution; Canadian rows exist, are kept, and "
        "are filterable. The geographic heatmap covers US states; Canadian provinces appear in "
        "tables and route analytics.",
        "4. **No carrier/cost-per-shipment field** — 'cost-time tradeoff' comparisons are "
        "descriptive (sales and margin by mode), per the spec's wording.",
        "5. **Efficiency ranking needs volume** — routes with < "
        f"{C.MIN_ROUTE_VOLUME_FOR_RANKING} lines are excluded from the min-max efficiency score "
        "(their raw stats are still listed).",
    ]
    (C.REPORTS_DIR / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"processed: {len(df):,} rows -> {C.PROCESSED_CSV}")
    print(f"report: {C.REPORTS_DIR / 'data_quality_report.md'}")


if __name__ == "__main__":
    main()
