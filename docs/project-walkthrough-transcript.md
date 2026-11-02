# Captioned project walkthrough

This is a screen recording of the browser companion, with on-screen explanation and no spoken narration.

## Project scope
10,194 synthetic order lines, five factories and 196 factory-to-state/province routes.

## Start with the date problem
Raw ship–order gaps are 904–1,642 days. The documented offset-and-modulo model derives a lead proxy, not independently confirmed true dates.

## Filter and compare
Shipping-mode, factory, state, region and order-date controls recompute the current population. Here we inspect Same Day.

## Rank routes carefully
Small routes stay visible but are not scored. Relative scores use routes with at least 20 lines in the selected population.

## Test the delay definition
Changing the delay threshold updates the rates and tables. It changes the reporting rule, not the underlying records.

## Inspect destinations
State/province comparisons include volume and recorded sales. They are not optimized road routes or causal explanations.

## Reproduce and review
The original Streamlit code is retained. This companion uses its cleaned analytical fields; the report states recovery and cost assumptions.
