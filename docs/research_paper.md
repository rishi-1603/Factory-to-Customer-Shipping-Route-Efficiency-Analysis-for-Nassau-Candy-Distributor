# Research Paper: Factory-to-Customer Shipping Route Efficiency Analysis for Nassau Candy Distributor

**Author:** Dappu Rishi Raghukumar — B.Tech CSE (Data Science), 2026
**Domain:** Logistics / Supply-Chain Analytics
**Dataset:** 10,194 order lines, 18 raw fields (supplied with the official project specification — synthetic, disclosed)

---

## Abstract

This study measures factory-to-customer shipping efficiency for Nassau Candy Distributor, a national
candy distributor shipping from 5 factories to customers across 59 US-state and Canadian-province
codes. Before any lead-time analysis, a **systematic timestamp defect** was detected: every ship
date sits 904-1,642 days after its order date in three bands exactly 365 days apart — a generative
multi-year offset, not shipping behaviour. We diagnose the defect's structure, recover true lead
times ((gap − 904) mod 365), and validate the recovery against ship-mode semantics (Same Day
median 0 < First/Second 3 < Standard 5 days, non-overlapping supports). On the recovered leads we
benchmark **196 factory-to-state routes**, finding a narrow efficiency band (route averages 3.4-5.0
days) against a wide mode band (0.4-5.3 days): **delay is driven by ship-mode choice, not
geography**. Standard Class carries 60.3% of sales at the slowest average (5.32 days) and the
highest delay frequency (38.8% over 5 days), while margins are uniform across modes (65.7-66.1%) —
mode selection is a service-level decision. We further identify 17 volume-weighted bottleneck
states (worst: Minnesota, 4.96 days) and a concentration risk: 96.6% of lines flow through 2 of 5
factories. All figures are computed from the data and pinned by 23 automated tests.

## 1. Introduction

Route-level efficiency intelligence — which lanes are fast, which lag, where congestion sits — is
the difference between reactive and data-driven logistics. The organization ships from 5 factories
(Lot's O' Nuts, Wicked Choccy's, Sugar Shack, Secret Factory, The Other Factory) whose products
reach customers in every US state and 10 Canadian provinces. The spec asks four questions: which
routes are consistently efficient, which are slow, how performance varies by region/state/mode,
and where bottlenecks exist.

## 2. Data quality first: the timestamp defect

Raw ship-order gaps of 904-1,642 days would rank routes by a defect. Decomposition shows the gap
= 904 + 365×K + true_lead with K ∈ {0,1,2} (observed counts 2,051 / 4,764 / 3,379) and true_lead
∈ [0, 11]. The recovery strips the whole-year blocks; its validity is enforced by a runtime
validation gate (ship-mode median ordering) that refuses to publish on violation, and by pinned
tests (recovered lead distribution, mode supports, year-block counts). The raw columns are
preserved for audit.

## 3. Method

Grain: order line. Route = Factory → State/Province (factory from the spec's product-factory
correlation). KPIs per the spec: lead time, average lead per route, route volume, delay frequency
(threshold 5 days default), and a route efficiency score (100 × (1 − normalized average lead),
restricted to routes with ≥ 20 lines to avoid small-sample artifacts — 75 of 196 routes rankable).
Bottlenecks: volume ≥ 50 lines AND above-median lead. Full formulas in docs/kpi_dictionary.md;
SQL mirrors in sql/.

## 4. Results

**Network:** average recovered lead 4.29 days (median 4, P90 7); 24.7% of lines exceed the 5-day
threshold; sales $141,783.63 at 65.9% margin.

**Routes:** fastest Lot's O' Nuts → Ontario (3.36 days, score 100); slowest Wicked Choccy's →
Indiana (5.04 days, 46.3% delay frequency, score 0). Route averages span 3.4-5.0 days — a 1.6-day
band.

**Modes:** averages span 0.4-5.3 days — **~2.4× the route spread**. Standard Class: 6,120 lines,
60.3% of sales, 5.32-day average, 38.8% delay frequency. Same Day and First Class: 0% delay
frequency. Margins uniform (65.7-66.1%).

**Bottlenecks:** 17 states combine volume ≥ 50 with above-median lead; worst are Minnesota
(4.96d), Tennessee (4.81d), New Jersey (4.75d), Indiana (4.71d).

**Concentration:** Lot's O' Nuts (55.8%) and Wicked Choccy's (40.7%) together carry 96.6% of all
lines.

**Regions:** Pacific (3,253 lines, 4.27d), Atlantic (2,986, 4.24d), Interior (2,335, 4.38d), Gulf
(1,620, 4.30d) — regional averages within 0.14 days of each other.

## 5. Discussion

The narrow route band and the wide mode band invert the usual logistics intuition: the network's
delay problem is a **mode-allocation problem**. Because margins are uniform, shifting eligible
volume from Standard to faster modes is a service decision without a margin penalty in this data.
The 96.6% two-factory concentration is the network's largest structural risk. The timestamp
defect itself is an operational finding: any KPI built on the raw dates (including the
organization's own reporting, if it shares the source) is unreliable until the upstream pipeline
is fixed.

## 6. Limitations

- Synthetic dataset (disclosed); real-world generalization requires validation.
- No carrier-cost field → the cost-time tradeoff is descriptive (sales/margin by mode).
- Ship dates are only usable through the validated recovery; no calendar-trend analysis of ship
  dates is meaningful.
- Canada (200 lines) is in scope for tables/routes but outside the spec's US heatmap.

## 7. Conclusion

With the defect caught, diagnosed and validated, the analysis delivers the spec's four answers:
route benchmarks (196 routes, scored), mode tradeoffs (Standard = 60% of sales at the slowest
speed), bottleneck geography (17 states, volume-weighted), and a concentration warning (96.6% on
two factories). Every number is reproducible: 23 pinned tests, deterministic CI-verified reports,
and a SQL layer mirroring the Python.
