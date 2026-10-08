# Resume bullets — verified numbers only

1. Caught a timestamp defect affecting all 10,194 shipment records before lead-time analysis was built on unreliable data — diagnosed the generative structure (3 bands exactly 365 days apart), recovered true lead times, and validated the recovery against ship-mode semantics (Same Day 0d < First/Second 3d < Standard 5d), with raw values preserved for audit.

2. Benchmarked 196 factory-to-state routes in pandas, finding 2 of 5 factories drive 96.6% of order volume — and that delay is mode-driven, not geography-driven: route averages span 3.4–5.0 days while ship modes span 0.4–5.3, with Standard Class carrying 60.3% of sales at the slowest speed (38.8% delay frequency at the 5-day threshold).

3. Analyzed $141.8K in sales across 4 regions and 4 shipping modes, identified 17 volume-weighted bottleneck states (worst: Minnesota, 4.96-day average), and shipped a 4-module Streamlit dashboard (route leaderboard, US efficiency heatmap with factory overlay, mode tradeoffs, state drill-down) with 23 pinned tests and a SQL layer mirroring every KPI.

## Shorter variants

- Caught a dataset-wide timestamp defect (2.5–4.5-year "lead times") before route analysis; recovered true lead times validated against ship-mode semantics, then benchmarked 196 factory-to-state routes across $141.8K of sales.
- Built a route-efficiency intelligence dashboard over 10,194 shipments: 196 routes benchmarked, 17 bottleneck states identified, mode-vs-geography delay decomposition, 23 pinned tests.
