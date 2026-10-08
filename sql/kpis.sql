-- KPI queries — mirror src/kpis.py exactly. All lead-time KPIs use the
-- RECOVERED lead (lead_time_days); the raw defective gap is never used.

-- KPI 1: network lead-time overview
-- Expected: avg 4.29, median 4, P90 7, range 0-11 (pinned in tests)
SELECT
    COUNT(*)                                            AS shipments,
    ROUND(AVG(lead_time_days), 2)                       AS avg_lead_days,
    ROUND(AVG(lead_time_days), 0)                       AS median_lead_days_approx,
    MIN(lead_time_days)                                 AS min_lead_days,
    MAX(lead_time_days)                                 AS max_lead_days,
    MIN(lead_time_raw_days)                             AS raw_gap_min,
    MAX(lead_time_raw_days)                             AS raw_gap_max
FROM shipments;

-- KPI 2 + 3 + 4 + 5: route table (volume, avg lead, delay freq, efficiency)
-- Efficiency score = 100 * (1 - (avg - min) / (max - min)) over routes with >= 20 lines.
-- Delay frequency uses the default 5-day threshold.
WITH route_stats AS (
    SELECT
        route,
        MIN(factory)                                    AS factory,
        MIN(state_province)                             AS state,
        COUNT(*)                                        AS volume,
        ROUND(AVG(lead_time_days), 2)                   AS avg_lead_days,
        ROUND(AVG(CASE WHEN lead_time_days > 5 THEN 1.0 ELSE 0.0 END) * 100, 1)
                                                        AS delay_freq_pct,
        SUM(sales)                                      AS sales
    FROM shipments
    GROUP BY route
),
rankable AS (
    SELECT * FROM route_stats WHERE volume >= 20
),
bounds AS (
    SELECT MIN(avg_lead_days) AS lo, MAX(avg_lead_days) AS hi FROM rankable
)
SELECT
    r.route,
    r.volume,
    r.avg_lead_days,
    r.delay_freq_pct,
    ROUND(100.0 * (1.0 - (r.avg_lead_days - b.lo) / (b.hi - b.lo)), 1) AS efficiency_score
FROM rankable r CROSS JOIN bounds b
ORDER BY efficiency_score DESC;

-- Ship-mode performance (mirrors ship_mode_performance)
SELECT
    ship_mode,
    COUNT(*)                                   AS volume,
    ROUND(AVG(lead_time_days), 2)              AS avg_lead_days,
    ROUND(SUM(sales), 2)                       AS sales,
    ROUND(100.0 * SUM(sales) / (SELECT SUM(sales) FROM shipments), 1) AS sales_share_pct,
    ROUND(100.0 * SUM(gross_profit) / SUM(sales), 1)                  AS profit_margin_pct,
    ROUND(AVG(CASE WHEN lead_time_days > 5 THEN 1.0 ELSE 0.0 END) * 100, 1) AS delay_freq_pct
FROM shipments
GROUP BY ship_mode
ORDER BY avg_lead_days;

-- Factory concentration (expected: top-2 = 96.6% of lines)
SELECT
    factory,
    COUNT(*)                                            AS volume,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM shipments), 1) AS volume_share_pct,
    ROUND(AVG(lead_time_days), 2)                       AS avg_lead_days,
    ROUND(SUM(sales), 2)                                AS sales
FROM shipments
GROUP BY factory
ORDER BY volume DESC;
