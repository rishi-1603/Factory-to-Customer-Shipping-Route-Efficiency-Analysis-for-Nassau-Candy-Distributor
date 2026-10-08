# Data Dictionary — Nassau Candy shipments

**Source:** `data/raw/nassau_candy_shipments.csv` (supplied with the official project spec; synthetic) →
cleaned to `data/processed/nassau_clean.csv`
**Grain:** one row = one **order line** (Row ID unique; Order ID repeats across lines)

## Raw fields (18, exactly as shipped)

| Column | Type | Description |
|---|---|---|
| Row ID | int | Unique row identifier |
| Order ID | text | Order identifier (8,549 unique — repeats across lines) |
| Order Date | date (DD-MM-YYYY) | Order placement date (2024-01-02 → 2025-12-31) |
| Ship Date | date (DD-MM-YYYY) | **DEFECTIVE as shipped** — 2026-06-30 → 2030-06-28; see derived fields |
| Ship Mode | text | Same Day / First Class / Second Class / Standard Class |
| Customer ID | int | 5,044 unique customers |
| Country/Region | text | United States (9,994) / Canada (200) |
| City | text | 542 cities |
| State/Province | text | 59 codes (US states + DC + Canadian provinces) |
| Postal Code | text | 654 codes |
| Division | text | Chocolate / Sugar / Other |
| Region | text | Atlantic / Gulf / Interior / Pacific |
| Product ID | text | 15 products |
| Product Name | text | e.g. "Wonka Bar - Milk Chocolate" |
| Sales | real | Line sales (positive; total $141,783.63) |
| Units | int | Units on the line |
| Gross Profit | real | Sales − Cost (identity verified on all rows) |
| Cost | real | Cost to manufacture |

## Derived columns (documented transformations)

| Column | Formula | Notes |
|---|---|---|
| order_date_parsed / ship_date_parsed | ISO parse (dayfirst) | DD-MM-YYYY ('30-06-2026' cannot be MM-DD) |
| lead_time_raw_days | ship − order, as shipped | **904-1,642 — the timestamp defect, never used for KPIs** |
| defect_year_blocks | (gap − 904) // 365 | K ∈ {0,1,2} — the whole-year blocks in the defect |
| lead_time_days | (gap − 904) mod 365 | **RECOVERED true lead, 0-11 days** — validated vs ship-mode semantics |
| Factory | Product Name → factory (spec correlation table) | 5 factories |
| route | "Factory → State/Province" | 196 unique routes |

## Reference data (from the spec)

- **Factory coordinates:** Lot's O' Nuts (32.88, −111.77) · Wicked Choccy's (32.08, −81.09) ·
  Sugar Shack (48.12, −96.18) · Secret Factory (41.45, −90.57) · The Other Factory (35.12, −89.97)
- **Product-factory correlation:** 15 products → 5 factories (encoded in `src/config.py::FACTORY_MAP`;
  chocolate Wonka Bars split between Lot's O' Nuts and Wicked Choccy's; sugar lines from Sugar
  Shack; the remainder from Secret Factory and The Other Factory)
