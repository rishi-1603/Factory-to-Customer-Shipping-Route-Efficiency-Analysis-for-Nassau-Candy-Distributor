# KPI Dictionary — formulas, bases, and defaults

| KPI | Formula | Basis | Default |
|---|---|---|---|
| **Shipping Lead Time** | recovered lead = (Ship − Order − 904) mod 365, days | per order line | — |
| **Average Lead Time** | mean(recovered lead) over scope | network / route / state / mode | — |
| **Route Volume** | count of order lines per route | per route (lines, not orders) | — |
| **Delay Frequency** | 100 × share of lines with lead > threshold | scope | threshold = 5 days (slider: 1-10) |
| **Route Efficiency Score** | 100 × (1 − (avg_lead − min)/(max − min)) over routes with ≥ 20 lines | per route | min volume = 20 lines |
| **Sales / Gross Profit** | Σ Sales, Σ Gross Profit over scope | scope | — |

## Design notes

- **Why recovered lead:** raw ship-order gaps are 904-1,642 days on all rows (the timestamp
  defect). See docs/methodology.md §2 for detection, diagnosis, recovery and the ship-mode
  validation gate.
- **Why threshold-default 5:** ≈ the 70th percentile of recovered leads (network delay
  frequency 24.7% at 5 days). Adjustable per the spec — the dashboard recomputes everything.
- **Why min-volume 20 for scoring:** min-max normalization over tiny samples produces fake
  100s and 0s. Small routes keep their raw stats in every table; they are only excluded from
  the score. 75 of 196 routes are rankable.
- **Why lines, not orders:** the grain is the order line; an Order ID legitimately spans
  multiple lines, and route-level volume semantics ("shipments on this lane") map to lines.

## Pinned values (test-enforced)

- Network: 10,194 lines · 8,549 orders · 5,044 customers · 196 routes · 59 state codes · 4 regions · 4 modes
- Lead: avg 4.29d · median 4 · P90 7 · range 0-11 · distribution pinned exactly
- Delay frequency @5d: 24.7%
- Modes: Same Day 0.38d · First 2.55d · Second 3.57d · Standard 5.32d (Standard = 60.3% of sales, 38.8% delay freq)
- Best route: Lot's O' Nuts → Ontario (3.36d, score 100); worst: Wicked Choccy's → Indiana (5.04d, score 0, 46.3% delay freq)
- Bottlenecks: 17 states (volume ≥50 & lead > median 4.355d); worst Minnesota 4.96d
- Factory concentration: top-2 = 96.6% of lines
- Financials: sales $141,783.63 · gross profit $93,442.80 · Gross Profit = Sales − Cost (all rows)
