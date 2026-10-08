"""Configuration: paths, constants, the factory map, and the defect model.

The timestamp defect (documented, detected, recovered — never silently fixed):
    Raw Ship Dates sit 904-1,642 days after Order Dates — impossible for candy
    distribution. The gap decomposes exactly into:

        gap = DEFECT_BASE_DAYS + 365 * K + true_lead
              (K ∈ {0,1,2}, true_lead ∈ [0, 11] days)

    i.e. every Ship Date carries a systematic multi-year offset (the generator
    added whole 365-day blocks). The recovery strips the offset:

        recovered_lead = (gap - DEFECT_BASE_DAYS) % 365

    and validates perfectly against ship-mode semantics (Same Day median 0,
    First Class 3, Second Class 3, Standard 5 — non-overlapping supports).
    The recovery is logged per transformation step and pinned by tests.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = REPO_ROOT / "data" / "raw" / "nassau_candy_shipments.csv"
PROCESSED_CSV = REPO_ROOT / "data" / "processed" / "nassau_clean.csv"
REPORTS_DIR = REPO_ROOT / "reports"

# ── Defect model (see module docstring) ─────────────────────────────────────
DEFECT_BASE_DAYS = 904      # minimum raw gap observed across all 10,194 rows
DEFECT_BLOCK_DAYS = 365     # the bands are exactly 365 days apart
RAW_GAP_MIN = 904
RAW_GAP_MAX = 1642

# ── Column names (kept exactly as shipped — no silent renames) ──────────────
COL_ROW_ID = "Row ID"
COL_ORDER_ID = "Order ID"
COL_ORDER_DATE = "Order Date"
COL_SHIP_DATE = "Ship Date"
COL_SHIP_MODE = "Ship Mode"
COL_CUSTOMER_ID = "Customer ID"
COL_COUNTRY = "Country/Region"
COL_CITY = "City"
COL_STATE = "State/Province"
COL_POSTAL = "Postal Code"
COL_DIVISION = "Division"
COL_REGION = "Region"
COL_PRODUCT_ID = "Product ID"
COL_PRODUCT_NAME = "Product Name"
COL_SALES = "Sales"
COL_UNITS = "Units"
COL_GROSS_PROFIT = "Gross Profit"
COL_COST = "Cost"

# Derived columns (prefixed to avoid clashing with raw names)
COL_LEAD_RAW = "lead_time_raw_days"        # Ship − Order, as shipped (defective)
COL_LEAD = "lead_time_days"                # recovered true lead time
COL_DEFECT_YEARS = "defect_year_blocks"    # K in the defect model
COL_FACTORY = "Factory"                    # derived from Product Name
COL_ROUTE = "route"                        # Factory → State/Province
COL_IS_DELAYED = "is_delayed"              # lead > threshold (threshold is a KPI arg)

# Raw date format: DD-MM-YYYY (e.g. '30-06-2026' — month 30 cannot exist)
DATE_DAYFIRST = True

# ── Product → Factory (from the official project specification) ─────────────
FACTORY_MAP = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Kazookles": "The Other Factory",
}

# ── Factory coordinates (from the official project specification) ───────────
FACTORY_COORDS = {
    "Lot's O' Nuts":     (32.881893, -111.768036),
    "Wicked Choccy's":   (32.076176, -81.088371),
    "Sugar Shack":       (48.119140, -96.181150),
    "Secret Factory":    (41.446333, -90.565487),
    "The Other Factory": (35.117500, -89.971107),
}

# ── KPI defaults ─────────────────────────────────────────────────────────────
# Delay threshold: a shipment is 'delayed' when its recovered lead time
# exceeds this many days. Default 5 ≈ the 70th percentile of recovered leads;
# adjustable in the dashboard per the spec.
DEFAULT_DELAY_THRESHOLD_DAYS = 5

# Routes with fewer lines than this are excluded from efficiency-score
# RANKING (still listed with their raw stats) — a 90% delay rate on 3
# shipments is not a route problem. Displayed routes keep their numbers.
MIN_ROUTE_VOLUME_FOR_RANKING = 20

SHIP_MODES = ["Same Day", "First Class", "Second Class", "Standard Class"]

# Expected ship-mode lead ordering — the validation gate for defect recovery.
# If recovery ever produces leads that violate this ordering, the pipeline
# must fail loudly rather than publish unreliable numbers.
EXPECTED_MODE_MEDIAN_ORDER = ["Same Day", "First Class", "Second Class", "Standard Class"]
