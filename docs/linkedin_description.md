# LinkedIn post (2,000 chars)

🚚 Before analyzing a single route, I had to catch a data defect that made every "lead time" in the dataset meaningless.

Project: Factory-to-Customer Shipping Route Efficiency for Nassau Candy Distributor (10,194 order lines, 5 factories, 59 state codes, 196 routes).

The catch: every ship date sat 904–1,642 days after its order date — a 2.5–4.5 year "lead time" for candy. Not outliers: 100% of rows. The diagnosis: the gaps clustered in 3 bands exactly 365 days apart — a systematic multi-year generation offset, not shipping behaviour.

The recovery: strip the year blocks, keep the 0–11 day residual. The validation that made it defensible: recovered leads respect ship-mode semantics exactly (Same Day median 0d < First/Second 3d < Standard 5d, non-overlapping supports). The pipeline refuses to publish if that ordering ever breaks — and the raw values stay in the data for audit.

What the recovered data says:

• Delay is mode-driven, not geography-driven: route averages span 3.4–5.0 days, ship modes span 0.4–5.3 days
• Standard Class carries 60.3% of sales at the slowest speed (5.32d avg, 38.8% over the 5-day threshold) — while Same Day and First Class run at 0% delay frequency
• Margins are uniform across modes (65.7–66.1%) — mode choice is a service decision, not a margin lever
• 17 volume-weighted bottleneck states (worst: Minnesota, 4.96d)
• 96.6% of all volume flows through just 2 of 5 factories — the network's biggest structural risk

Stack: Python · pandas · Plotly · Streamlit · SQL (KPI mirrors) · 23 pinned tests incl. the defect structure and recovery distribution · deterministic CI-verified reports · 4-module dashboard with date/region/state/mode filters and an adjustable delay threshold.

Data-quality work isn't a pre-step to analysis. Here, it WAS the analysis — every downstream number depends on catching that defect first.

🔗 GitHub: https://github.com/rishi-1603/Factory-to-Customer-Shipping-Route-Efficiency-Analysis-for-Nassau-Candy-Distributor

#DataAnalytics #SupplyChain #Logistics #Python #Streamlit #DataQuality
