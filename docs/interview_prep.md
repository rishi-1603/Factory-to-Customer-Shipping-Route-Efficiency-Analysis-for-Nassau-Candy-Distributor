# Interview Prep — 60-second walkthrough + the hard questions

## Core project explanation (30 seconds)

"I analyzed factory-to-customer shipping for Nassau Candy, 10,194 order lines across 5 factories
and 59 state codes. The first thing I found was a timestamp defect: every single ship date sat
2.5 to 4.5 years after its order date. I diagnosed the structure — the gaps fell in bands exactly
365 days apart, a systematic multi-year offset — recovered the true lead times, and validated the
recovery against ship-mode semantics before building anything on it. Then I benchmarked 196
factory-to-state routes: the headline is that delay is driven by mode choice, not geography —
route averages span 3.4 to 5 days, but ship modes span 0.4 to 5.3. Standard Class carries 60% of
sales at the slowest speed and 38.8% delay frequency, and 96.6% of volume flows through just 2 of
5 factories."

## The defect questions (expect them)

**"How did you find the defect?"**
Descriptives first: min/max of ship minus order. Max of 1,642 days on a candy shipment is
impossible — and it was on 100% of rows, so it wasn't outliers. Then value counts of the gap:
only 28 unique values in 3 tight bands exactly 365 apart. That structure is generative, not real.

**"How do you know your recovery is right?"**
Three gates: (1) the decomposition is exact — (gap − 904) mod 365 lands every row in 0-11 days,
no stragglers; (2) semantic validation — recovered leads order by ship mode with non-overlapping
supports (Same Day max 2d, Standard min 3d), which is exactly how carriers price tiers; (3) the
pipeline enforces it — clean() raises if the ordering ever breaks, and tests pin the distribution.
Plus the raw columns stay in the data for audit.

**"What if the bands weren't exactly 365 apart?"**
Then the mod-recovery wouldn't be exact and I wouldn't use it — I'd report the defect, exclude
lead-time KPIs, and benchmark on volume/financial dimensions only. Publishing unreliable numbers
beats no numbers only in the short term.

## KPI questions

**"Why 5 days for the delay threshold?"** ~P70 of recovered leads; the dashboard exposes it as a
slider, and KPIs recompute. At 4 days delay frequency rises; the ranking is stable.

**"Why exclude small routes from the efficiency score?"** Min-max normalization over a 3-line
route produces fake 100s and 0s. Routes under 20 lines keep raw stats everywhere; only the score
excludes them (75 of 196 rankable).

**"Best and worst route?"** Lot's O' Nuts → Ontario 3.36d (score 100); Wicked Choccy's → Indiana
5.04d with 46.3% of lines over 5d (score 0).

## Findings questions

**"So is geography irrelevant?"** No — 17 states are volume-weighted bottlenecks (Minnesota worst
at 4.96d). But regional averages sit within 0.14 days of each other, while mode averages span
4.9 days. If you can only fix one lever, it's mode allocation.

**"Margin implication of shifting modes?"** None visible in this data — margins are 65.7-66.1%
across all modes. It's a service-level decision. (Limitation: no carrier-cost field, so this is
descriptive.)

**"Biggest risk?"** Concentration: 96.6% of lines on 2 of 5 factories. Any disruption at the
chocolate factories is a network-level event.

## Scope/honesty questions

- **Grain:** order line — Order IDs repeat; volumes are lines, never orders.
- **Canada:** 200 lines, kept and filterable; the spec's heatmap is US-only.
- **Synthetic data:** disclosed everywhere; the methods are the story.
- **Tests:** 23 — the defect structure, the recovery distribution, mode validation, every KPI
  pinned, plus an AppTest that renders the dashboard and checks the header numbers.
