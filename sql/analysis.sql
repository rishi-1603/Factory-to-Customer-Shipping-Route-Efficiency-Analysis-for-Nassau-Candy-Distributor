-- Analysis queries — geographic bottlenecks, state drill-down, timeline.

-- State-level performance (mirrors state_performance)
SELECT
    state_province                       AS state,
    COUNT(*)                             AS volume,
    ROUND(AVG(lead_time_days), 2)        AS avg_lead_days,
    ROUND(AVG(CASE WHEN lead_time_days > 5 THEN 1.0 ELSE 0.0 END) * 100, 1) AS delay_freq_pct,
    COUNT(DISTINCT factory)              AS factories_served,
    COUNT(DISTINCT route)                AS routes,
    ROUND(SUM(sales), 2)                 AS sales
FROM shipments
GROUP BY state_province
ORDER BY avg_lead_days DESC;

-- Geographic bottlenecks: volume >= 50 AND above-median average lead
-- (mirrors detect_bottlenecks; expected: 17 states, worst Minnesota 4.96d)
WITH state_stats AS (
    SELECT
        state_province AS state,
        COUNT(*)        AS volume,
        ROUND(AVG(lead_time_days), 2) AS avg_lead_days
    FROM shipments
    GROUP BY state_province
),
med AS (SELECT AVG(avg_lead_days) AS m FROM state_stats WHERE volume >= 50)
SELECT s.*
FROM state_stats s CROSS JOIN med
WHERE s.volume >= 50 AND s.avg_lead_days > med.m
ORDER BY s.avg_lead_days DESC;

-- State drill-down: routes serving one state (example: Indiana)
SELECT
    route,
    COUNT(*)                      AS volume,
    ROUND(AVG(lead_time_days), 2) AS avg_lead_days,
    ROUND(SUM(sales), 2)          AS sales
FROM shipments
WHERE state_province = 'Indiana'
GROUP BY route
ORDER BY avg_lead_days;

-- Order-level shipment timeline (50 most recent lines for a state)
SELECT
    order_id,
    order_date_parsed,
    ship_date_parsed,
    lead_time_days,
    lead_time_raw_days,   -- audit trail: the defective raw gap, kept visible
    ship_mode,
    factory,
    product_name,
    sales
FROM shipments
WHERE state_province = 'Indiana'
ORDER BY order_date_parsed DESC
LIMIT 50;

-- Region performance (expected: Pacific 3,253 lines / $46,301.53 — largest)
SELECT
    region,
    COUNT(*)                      AS volume,
    ROUND(AVG(lead_time_days), 2) AS avg_lead_days,
    ROUND(SUM(sales), 2)          AS sales,
    ROUND(SUM(gross_profit), 2)   AS profit,
    COUNT(DISTINCT state_province) AS states
FROM shipments
GROUP BY region
ORDER BY volume DESC;

-- The timestamp defect, in one query: banded raw gaps exactly 365 apart
SELECT
    (lead_time_raw_days - 904) / 365 AS defect_year_blocks,
    COUNT(*)                          AS rows,
    MIN(lead_time_raw_days)           AS gap_min,
    MAX(lead_time_raw_days)           AS gap_max,
    MIN(lead_time_days)               AS recovered_lead_min,
    MAX(lead_time_days)               AS recovered_lead_max
FROM shipments
GROUP BY defect_year_blocks
ORDER BY defect_year_blocks;
