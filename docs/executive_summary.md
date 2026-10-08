# Executive Summary — Factory-to-Customer Shipping Route Efficiency
**Nassau Candy Distributor** · 10,194 order lines · 196 routes · 5 factories · 59 state/province codes
*All lead-time figures use the recovered lead (the timestamp defect is documented below and in reports/data_quality_report.md).*

---

## 1. Network performance

| Metric | Value |
|---|---|
| Average shipping lead time | **4.29 days** (median 4, P90 7, range 0-11) |
| Delay frequency (default 5-day threshold) | **24.7%** of lines |
| Total sales on the network | **$141,783.63** (margin 65.9%) |
| Routes benchmarked | 196 (75 with ≥20 lines are efficiency-scored) |

## 2. What the data quality work found first

The raw ship dates carried a **systematic multi-year timestamp defect** (gaps of 904-1,642 days on
every row). Every lead-time figure in this analysis uses a **recovered** lead, validated against
ship-mode semantics (Same Day 0d < First/Second 3d < Standard 5d). Raw values are preserved for
audit. **Recommendation: fix the source date pipeline.**

## 3. Route efficiency

- **Fastest rankable route:** Lot's O' Nuts → Ontario — **3.36 days** average (score 100)
- **Slowest:** Wicked Choccy's → Indiana — **5.04 days** average, 46.3% of lines over 5 days (score 0)
- Route averages span a **narrow band (3.4-5.0 days)** — geography is not the main story

## 4. The dominant finding: mode choice, not geography

| Mode | Avg lead | Lines | Sales share | Delay freq (>5d) |
|---|---|---|---|---|
| Same Day | 0.38d | 547 | 5.0% | 0.0% |
| First Class | 2.55d | 1,548 | 15.0% | 0.0% |
| Second Class | 3.57d | 1,979 | 19.6% | 7.5% |
| **Standard Class** | **5.32d** | **6,120** | **60.3%** | **38.8%** |

Mode averages span **0.4-5.3 days — ~2.4× the route spread**. Standard Class carries 60% of sales
at the slowest speed; fast options already exist in-network. Margins are uniform (65.7-66.1%),
so mode selection is a service-level decision, not a margin lever.

## 5. Geographic bottlenecks

17 states combine volume ≥ 50 lines with above-median lead times — worst: **Minnesota (4.96d,
31.5%), Tennessee (4.81d, 35.0%), New Jersey (4.75d, 35.4%), Indiana (4.71d, 34.2%)**.

## 6. Concentration risk

**96.6% of all order lines flow through just 2 of 5 factories** (Lot's O' Nuts 55.8%, Wicked
Choccy's 40.7%). A disruption at either chocolate factory affects nearly the entire network.

## 7. Recommendations

| Priority | Action | Basis |
|---|---|---|
| 🔴 HIGH | Fix the upstream ship-date pipeline | 100% of rows defective; recovery is validated but the source is broken |
| 🔴 HIGH | Audit 5-day+ Standard Class flows | 38.8% of Standard lines exceed 5d; in-network fast options exist |
| 🟡 MED | Review the 17 bottleneck states, starting with Minnesota | Volume + above-median lead |
| 🟡 MED | Assess concentration risk on the 2 chocolate factories | 96.6% of volume |
| 🟢 LOW | Regional rebalancing | Regional averages are within 0.14d of each other |
