# Factory-to-Customer Shipping Route Efficiency

A synthetic Nassau Candy case study with an explicit timestamp-recovery assumption

**Author:** Dappu Rishi Raghukumar
**Project/reporting date:** 23 September 2026
**Web edition prepared:** 2 November 2026
**Status:** Unpublished project technical report; not peer-reviewed or independently approved.

## Abstract
This project reviews 10,194 synthetic order lines linking five named factories to state/province destinations. All supplied ship dates follow order dates by implausible multi-year intervals. The original project derives a 0-11 day lead-time proxy using an offset-and-modulo model and checks its consistency against shipping-mode patterns. This report retains that analytical scenario while distinguishing internal consistency from proof of the true dates. The browser companion supports route, shipping-mode, state/province, order-date and delay-threshold exploration.

## Results
- Order lines: 10,194
- Factories / state-province codes: 5 / 59
- Factory-to-state routes: 196
- Routes with at least 20 lines: 75
- Mean recovered lead proxy: 4.29 days
- Median / P90 lead proxy: 4 / 7 days
- Above 5-day threshold: 24.7%
- Recorded sales / gross profit: USD 141,783.63 / USD 93,442.80

## 1. Business question and grain
The project compares factory-to-state/province routes and shipping modes, with order-line volume shown alongside timing summaries. A route is a factory-destination combination, not an inferred road path or an optimized transport itinerary. The data is synthetic and supplied for a project case; it does not establish actual Nassau Candy operations.

## 2. Timestamp issue and recovery model
Raw ship-minus-order gaps range from 904 to 1,642 days. The project assumes gap = 904 + 365K + lead, with K in {0,1,2}, and computes a lead proxy as (gap - 904) mod 365. Raw dates and gaps remain preserved. The derived values fall between zero and eleven days and exhibit the documented mode ordering. Those checks establish internal consistency with the assumed model, not independent evidence that the recovered values are the true shipment durations. Source-owner confirmation or a timestamp oracle would be required for that stronger claim.

## 3. Metrics and comparisons
Mean lead and delay shares are computed per order line. The default delay threshold is greater than five days and is adjustable in the companion. Route ranking is restricted to at least twenty lines; smaller routes remain visible without a score. Relative efficiency rescales route means within the eligible filtered population, so a score is not an absolute service-level guarantee.

## 4. Findings
Under the recovery assumption, average lead is 4.29 days and 24.7% of lines exceed five days. Shipping-mode averages vary more than the reported route averages. Standard Class carries approximately 60.3% of sales and has a mean proxy lead of 5.32 days. Recorded gross margins are similar across modes, but there is no carrier-cost field establishing that switching modes would have no financial penalty. The route comparison is descriptive rather than a causal service recommendation.

## 5. Concentration and geographic scope
Approximately 96.6% of lines are associated with two factories. The scope includes US states and Canadian provinces, including 200 Canadian lines. The browser companion provides state/province comparisons rather than implying a road-network routing model. Low-volume destinations need caution.

## 6. Demonstration and reproducibility
The original Python Streamlit dashboard is retained. The browser companion uses only analytical dimensions, dates, the lead proxy, sales and profit; it omits customer names, identifiers, order IDs, city and address fields. scripts/build_web_data.py recreates the export through the existing pipeline. Filters, route tables, mode comparisons and CSV downloads are available without an account or API key.

## 7. Limitations and next validation
The recovery formula is conditional, not an independently certified correction to actual business timestamps. There is no measured causal effect, actual carrier-charge comparison or observed savings. Before operational use, repair timestamps upstream, define service targets, confirm route grain and data permissions, and validate the ranking against real operating outcomes.

## Sources
https://github.com/rishi-1603/Factory-to-Customer-Shipping-Route-Efficiency-Analysis-for-Nassau-Candy-Distributor
See the repository methodology, KPI dictionary, original analysis and data-quality reports.
