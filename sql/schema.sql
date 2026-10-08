-- Schema: Nassau Candy shipments (raw fields as shipped + derived analytical columns)
-- SQLite/PostgreSQL-compatible. Mirrors src/data_cleaning.py.

CREATE TABLE shipments (
    row_id            INTEGER PRIMARY KEY,       -- unique row identifier
    order_id          TEXT NOT NULL,             -- order identifier (repeats across lines)
    order_date        TEXT NOT NULL,             -- DD-MM-YYYY as shipped
    ship_date         TEXT NOT NULL,             -- DD-MM-YYYY as shipped (defective — see below)
    ship_mode         TEXT NOT NULL,             -- Same Day | First Class | Second Class | Standard Class
    customer_id       INTEGER NOT NULL,
    country           TEXT NOT NULL,             -- United States | Canada
    city              TEXT NOT NULL,
    state_province    TEXT NOT NULL,             -- 59 US-state + Canadian-province codes
    postal_code       TEXT,
    division          TEXT NOT NULL,             -- Chocolate | Sugar | Other
    region            TEXT NOT NULL,             -- Atlantic | Gulf | Interior | Pacific
    product_id        TEXT NOT NULL,
    product_name      TEXT NOT NULL,
    sales             REAL NOT NULL, CHECK (sales > 0),
    units             INTEGER NOT NULL,
    gross_profit      REAL NOT NULL,             -- verified identity: sales - cost
    cost              REAL NOT NULL,
    -- ── derived (documented transformations, see reports/data_quality_report.md) ──
    order_date_parsed DATE,                      -- ISO date
    ship_date_parsed  DATE,
    lead_time_raw_days INTEGER,                  -- ship - order AS SHIPPED (defective: 904-1642)
    defect_year_blocks INTEGER,                  -- K in gap = 904 + 365*K + true_lead
    lead_time_days    INTEGER,                   -- RECOVERED true lead (0-11), validated vs ship mode
    factory           TEXT NOT NULL,             -- from product-factory correlation (spec)
    route             TEXT NOT NULL              -- 'factory -> state_province'
);

CREATE INDEX idx_shipments_route ON shipments(route);
CREATE INDEX idx_shipments_mode  ON shipments(ship_mode);
CREATE INDEX idx_shipments_state ON shipments(state_province);
