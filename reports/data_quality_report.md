# Data Quality Report

Source: `data/raw/nassau_candy_shipments.csv` → Processed: `data/processed/nassau_clean.csv`

## Transformation log

| Step | Detail |
|---|---|
| load | 10,194 rows × 18 columns read |
| whitespace | stripped leading/trailing whitespace in 0 cell(s) across text columns |
| duplicates | 0 exact duplicate rows, 0 duplicate Row IDs (expected 0; nothing deleted) |
| date_parsing | Order Date and Ship Date parsed as DD-MM-YYYY (0 failures). Order range 2024-01-02 → 2025-12-31; Ship range 2026-06-30 → 2030-06-28 |
| defect_detection | ALL 10,194 ship dates are 904-1642 days after order dates (28 unique gaps in 3 bands exactly 365 days apart) — a systematic multi-year generation offset, not real lead times |
| defect_recovery | recovered true lead = (gap − 904) mod 365; year-blocks stripped: K=0: 2,051, K=1: 4,764, K=2: 3,379; raw columns preserved for audit |
| recovery_validation | recovered leads respect ship-mode semantics — medians: First Class 3d, Same Day 0d, Second Class 3d, Standard Class 5d; Same Day max 2d |
| factory_mapping | Factory derived from Product Name via the spec's correlation table (5 factories); raw Product columns preserved |
| route_definition | route = Factory → Customer State/Province; 196 unique routes across 5 factories and 59 state/province codes |
| financial_validation | Gross Profit == Sales − Cost for all rows (max deviation 7.1e-15); 0 non-positive sales; total sales $141,783.63 |
| geographic_scope | countries: Canada, United States — 200 Canadian rows kept and filterable (the spec's heatmap covers US states; Canadian provinces appear in tables and route analytics) |
| missing_values | none — 0 missing cells across all columns |
| write | processed dataset written to nassau_clean.csv |

## Dataset profile

- Rows: 10,194 (order-line grain; 8,549 unique orders)
- Columns: 25 (18 raw + 7 derived)
- Factories: 5 | Products: 15 | State/province codes: 59 | Regions: 4
- Unique routes (Factory → State): 196
- Total sales: $141,783.63 | Gross profit: $93,442.80

## The timestamp defect (the most important data-quality finding)

ALL 10,194 ship dates sit 904-1642 days after their order dates — an impossible 2.5-4.5 year 'lead time' for candy distribution. The gap decomposes exactly into `904 + 365×K + true_lead` (K ∈ {0,1,2}, true lead 0-11 days): a systematic multi-year generation offset. Recovery strips the offset and is validated against ship-mode semantics (Same Day median 0 < First Class 3 ≈ Second Class 3 < Standard 5). Raw columns (`lead_time_raw_days`, both date columns) are preserved so every recovered number is auditable.

## Known limitations (documented, not 'fixed')

1. **Ship dates are defective as shipped** — all lead-time KPIs use the *recovered* lead, with the defect model, validation and per-row audit trail above.
2. **Order-line grain** — an Order ID can span multiple lines; route volumes count lines, not orders (documented).
3. **US + Canada** — the spec targets US distribution; Canadian rows exist, are kept, and are filterable. The geographic heatmap covers US states; Canadian provinces appear in tables and route analytics.
4. **No carrier/cost-per-shipment field** — 'cost-time tradeoff' comparisons are descriptive (sales and margin by mode), per the spec's wording.
5. **Efficiency ranking needs volume** — routes with < 20 lines are excluded from the min-max efficiency score (their raw stats are still listed).