# Methodology

## 1. The analytical question

Nassau Candy Distributor ships from 5 factories to customers across US states (and some Canadian
provinces). The organization lacks route-level efficiency intelligence: which factory-to-customer
routes are consistently fast, which lag, how performance varies by region/state/mode, and where
the geographic bottlenecks are. This project turns 10,194 order lines into that intelligence.

## 2. THE TIMESTAMP DEFECT (the most important call in the project)

**Detected:** 100% of the 10,194 ship dates sit **904-1,642 days** after their order dates — an
impossible 2.5-4.5 year "lead time" for candy distribution. Building route KPIs on the raw dates
would have produced garbage ranked by a defect.

**Diagnosed:** the raw gap is not noise — it has exact structure. All 10,194 gaps fall into
3 bands exactly **365 days apart**, with a small residual:

```
gap = 904 + 365 × K + true_lead     K ∈ {0,1,2}, true_lead ∈ [0, 11] days
```

This is the signature of a systematic multi-year generation offset (whole 365-day blocks added
to the ship dates), not of real shipping behaviour.

**Recovered:** `recovered_lead = (gap − 904) mod 365` — strips the defect, preserves the
0-11 day residual.

**Validated (the gate that makes this defensible):** recovered leads respect ship-mode
semantics exactly — medians: Same Day 0 < First Class 3 ≈ Second Class 3 < Standard Class 5,
with non-overlapping supports (Same Day max 2 days; Standard min 3 days). If a future data
refresh ever violates this ordering, `clean()` raises and the pipeline refuses to publish.

**Auditable:** the raw columns (`lead_time_raw_days`, both original date columns) are preserved
in the processed dataset; the dashboard's drill-down shows the raw gap alongside the recovered
lead on hover. Nothing is silently "fixed".

## 3. Grain

One row = one **order line** (Row ID). Order IDs repeat (8,549 unique orders across 10,194
lines) — multi-line orders exist, so route volumes count **lines**, never orders. All rates are
documented per-line.

## 4. Route definition

`route = Factory → Customer State/Province` (per the spec). The factory is derived from the
product via the spec's product-factory correlation table (all 15 products map to exactly one of
5 factories). Result: **196 unique routes**.

## 5. KPI definitions (see docs/kpi_dictionary.md for formulas)

1. **Shipping Lead Time** — the recovered lead (Section 2), per line.
2. **Average Lead Time** — mean recovered lead per scope (network / route / state / mode).
3. **Route Volume** — lines per route.
4. **Delay Frequency** — share of lines above the delay threshold (default 5 days, adjustable).
5. **Route Efficiency Score** — 100 × (1 − normalized avg lead) over routes with ≥ 20 lines;
   fastest rankable route = 100, slowest = 0. Routes under 20 lines keep their raw stats but
   are excluded from scoring (a 100% delay rate on 3 lines is not a route problem).

## 6. Bottleneck definition

A state is a bottleneck when it has **volume ≥ 50 lines AND above-median average lead** — the
spec's "high shipment volume + poor performance" condition. Result: 17 states, worst Minnesota
(4.96d avg, 31.5% delay frequency).

## 7. Scope decisions (documented, not hidden)

- **US + Canada:** the spec targets US distribution; 200 Canadian lines exist, are kept, and
  are filterable. The heatmap covers US states (per the spec); Canadian provinces appear in
  tables and route analytics.
- **Cost-time tradeoff is descriptive:** the dataset has no carrier-cost field, so mode
  comparisons use sales/margin by mode (margins are uniform 65.7-66.1% — mode choice is a
  service-level decision, not a margin lever).
- **Dates:** order dates span 2024-01-02 → 2025-12-31 (2 years) — the date-range filter uses
  these; ship dates are only used through the recovered lead.

## 8. Reproducibility

Every headline number is computed by `src/kpis.py` / `src/analytics.py` and pinned by 23
tests. The pipeline is deterministic (CI re-runs it and fails if reports drift by a byte).
SQL mirrors of every KPI live in `sql/`.
