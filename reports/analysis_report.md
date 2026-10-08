# Analysis Report — Factory-to-Customer Shipping Route Efficiency

Nassau Candy Distributor · 10,194 order lines · 196 routes · all lead-time figures use the RECOVERED lead (timestamp defect documented in the data quality report)

## 1. Network lead-time performance

- Average recovered lead time: **4.29 days** (median 4, P90 7, range 0-11 days)
- Delay frequency at the default 5-day threshold: **24.7%** of lines
- Raw ship-order gaps as shipped: 904-1642 days — the documented timestamp defect, never used for KPIs

## 2. Route efficiency leaderboard (routes with ≥ 20 lines; 75 of 196 routes rankable)

### Top 10 most efficient

| Route | Volume | Avg lead (d) | Delay freq | Efficiency score |
|---|---|---|---|---|
| Lot's O' Nuts → Ontario | 28 | 3.36 | 0.0% | 100.0 |
| Lot's O' Nuts → Louisiana | 24 | 3.54 | 4.2% | 89.3 |
| Lot's O' Nuts → Rhode Island | 30 | 3.57 | 16.7% | 87.5 |
| Lot's O' Nuts → Nebraska | 23 | 3.65 | 0.0% | 82.7 |
| Wicked Choccy's → Alabama | 22 | 3.73 | 9.1% | 78.0 |
| Wicked Choccy's → Rhode Island | 21 | 3.76 | 23.8% | 76.2 |
| Wicked Choccy's → Ohio | 189 | 3.80 | 17.5% | 73.8 |
| Lot's O' Nuts → Ohio | 262 | 3.82 | 22.9% | 72.6 |
| The Other Factory → California | 21 | 3.86 | 19.0% | 70.2 |
| Wicked Choccy's → Connecticut | 31 | 3.87 | 25.8% | 69.6 |

### Bottom 10 least efficient

| Route | Volume | Avg lead (d) | Delay freq | Efficiency score |
|---|---|---|---|---|
| Wicked Choccy's → Indiana | 54 | 5.04 | 46.3% | 0.0 |
| Lot's O' Nuts → Minnesota | 43 | 5.00 | 25.6% | 2.4 |
| Wicked Choccy's → Quebec | 24 | 5.00 | 20.8% | 2.4 |
| Wicked Choccy's → Minnesota | 45 | 4.91 | 37.8% | 7.7 |
| Wicked Choccy's → Tennessee | 67 | 4.91 | 35.8% | 7.7 |
| Lot's O' Nuts → New Jersey | 65 | 4.89 | 40.0% | 8.9 |
| Lot's O' Nuts → Oklahoma | 41 | 4.78 | 41.5% | 15.5 |
| Lot's O' Nuts → Utah | 29 | 4.76 | 27.6% | 16.7 |
| Lot's O' Nuts → Tennessee | 109 | 4.76 | 33.9% | 16.7 |
| Lot's O' Nuts → Alabama | 34 | 4.74 | 29.4% | 17.9 |

## 3. The dominant finding: mode choice, not geography

- Route averages span a narrow band (3.4-5.0 days among rankable routes); ship-mode averages span 0.4-5.3 days — **mode spread is ~2.9× the route spread**
- Standard Class carries **60.3% of sales** at the slowest average lead (5.32 days) and the highest delay frequency (38.8% at 5d)
- Profit margins are uniform across modes (65.7-66.1%) — mode choice is a service-level decision, not a margin lever

## 4. Geographic bottlenecks (volume ≥ 50 lines AND avg lead > median 4.36d)

| State/Province | Volume | Avg lead (d) | Delay freq | Factories served |
|---|---|---|---|---|
| Minnesota | 89 | 4.96 | 31.5% | 3 |
| Tennessee | 183 | 4.81 | 35.0% | 5 |
| New Jersey | 130 | 4.75 | 35.4% | 5 |
| Indiana | 149 | 4.71 | 34.2% | 4 |
| Oklahoma | 66 | 4.71 | 39.4% | 2 |
| Utah | 53 | 4.66 | 26.4% | 3 |
| Quebec | 50 | 4.64 | 22.0% | 3 |
| Oregon | 124 | 4.60 | 33.9% | 4 |
| Arkansas | 60 | 4.57 | 38.3% | 3 |
| Delaware | 96 | 4.55 | 32.3% | 5 |
| Missouri | 66 | 4.50 | 24.2% | 3 |
| Mississippi | 53 | 4.45 | 28.3% | 3 |
| Illinois | 492 | 4.45 | 23.8% | 4 |
| Washington | 506 | 4.38 | 27.9% | 5 |
| Arizona | 224 | 4.37 | 31.2% | 5 |
| New York | 1,128 | 4.37 | 27.6% | 5 |
| Michigan | 255 | 4.36 | 32.2% | 4 |

## 5. Factory concentration

**2 of 5 factories — Lot's O' Nuts and Wicked Choccy's — carry 96.6% of all order lines.** Network risk is concentrated: a disruption at either chocolate factory affects nearly the entire distribution network.

| Factory | Volume | Share | Avg lead (d) | Sales | Margin |
|---|---|---|---|---|---|
| Lot's O' Nuts | 5,692 | 55.8% | 4.26 | $76,340.15 | 69.1% |
| Wicked Choccy's | 4,152 | 40.7% | 4.35 | $55,352.75 | 65.1% |
| Secret Factory | 217 | 2.1% | 4.09 | $8,587.50 | 50.6% |
| The Other Factory | 100 | 1.0% | 3.98 | $1,282.25 | 11.9% |
| Sugar Shack | 33 | 0.3% | 4.67 | $220.98 | 54.9% |

## 6. Regions

| Region | Volume | Avg lead (d) | Sales | States |
|---|---|---|---|---|
| Pacific | 3,253 | 4.27 | $46,301.53 | 14 |
| Atlantic | 2,986 | 4.24 | $41,197.24 | 20 |
| Interior | 2,335 | 4.38 | $32,037.60 | 14 |
| Gulf | 1,620 | 4.30 | $22,247.26 | 11 |

## 7. Recommendations

1. **Audit the 5-day+ Standard Class flows** — 38.8% of Standard lines exceed 5 days; expedited options exist in-network (Same Day/First Class avg 0.4-2.6 days).
2. **Watch the 17 bottleneck states** (volume ≥ 50 AND above-median lead) — starting with Minnesota (4.96d avg, 31.5% delay freq).
3. **Concentration risk** — 96.6% of volume sits on 2 of 5 factories; diversify or stock-buffer the chocolate factories.
4. **Fix the upstream date pipeline** — the timestamp defect makes raw lead times unusable; the recovery here is validated, but the source system should be corrected.

---

All figures computed by `src/kpis.py` and `src/analytics.py` from `data/processed/nassau_clean.csv`; pinned by the test suite. Delay threshold: 5 days (default, adjustable). Efficiency score: 100 × (1 − normalized avg lead) over routes with ≥ 20 lines.