"""KPI tests — every dashboard number pinned to the dataset."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config as C, kpis, analytics  # noqa: E402


# ── KPI 1 ────────────────────────────────────────────────────────────────────

def test_kpi1_lead_overview_pinned(df):
    r = kpis.lead_time_overview(df)
    assert r["shipments"] == 10_194
    assert r["avg_lead_days"] == 4.29
    assert r["median_lead_days"] == 4
    assert r["p90_lead_days"] == 7
    assert r["min_lead_days"] == 0 and r["max_lead_days"] == 11
    assert r["raw_gap_min_days"] == 904 and r["raw_gap_max_days"] == 1642


# ── KPI 2-5: routes ──────────────────────────────────────────────────────────

def test_route_table_shape_and_rankability(df):
    routes = kpis.route_table(df)
    assert len(routes) == 196
    assert int(routes["rankable"].sum()) == 75  # volume >= 20 lines
    # efficiency scores bounded, only on rankable routes
    assert routes.loc[routes["rankable"], "efficiency_score"].between(0, 100).all()
    assert routes.loc[~routes["rankable"], "efficiency_score"].isna().all()


def test_leaderboard_extremes_pinned(df):
    routes = kpis.route_table(df)
    lb = kpis.route_leaderboard(routes)
    best = lb["most_efficient"].iloc[0]
    worst = lb["least_efficient"].iloc[0]
    assert best[C.COL_ROUTE] == "Lot's O' Nuts → Ontario"
    assert best["avg_lead_days"] == 3.36 and best["efficiency_score"] == 100.0
    assert worst[C.COL_ROUTE] == "Wicked Choccy's → Indiana"
    assert worst["avg_lead_days"] == 5.04 and worst["efficiency_score"] == 0.0
    assert worst["delay_freq_pct"] == 46.3


def test_delay_frequency_pinned(df):
    # network-level delay frequency at the default 5-day threshold
    assert round((df[C.COL_LEAD] > 5).mean() * 100, 1) == 24.7
    # threshold sensitivity: at 4 days it must be higher
    routes4 = kpis.route_table(df, threshold_days=4)
    assert (routes4["delay_freq_pct"] >= kpis.route_table(df)["delay_freq_pct"]).all()


# ── Ship mode ────────────────────────────────────────────────────────────────

def test_ship_mode_performance_pinned(df):
    m = kpis.ship_mode_performance(df).set_index(C.COL_SHIP_MODE)
    assert float(m.loc["Same Day", "avg_lead_days"]) == 0.38
    assert float(m.loc["First Class", "avg_lead_days"]) == 2.55
    assert float(m.loc["Second Class", "avg_lead_days"]) == 3.57
    assert float(m.loc["Standard Class", "avg_lead_days"]) == 5.32
    assert int(m.loc["Standard Class", "volume"]) == 6120
    assert float(m.loc["Standard Class", "sales_share_pct"]) == 60.3
    assert float(m.loc["Standard Class", "delay_freq_pct"]) == 38.8
    # margins uniform — the 'mode is a service decision' finding
    assert (m["profit_margin_pct"].between(65, 67)).all()


# ── Geography ────────────────────────────────────────────────────────────────

def test_state_performance_and_bottlenecks(df):
    sp = kpis.state_performance(df)
    assert len(sp) == 59
    bott, med = kpis.detect_bottlenecks(sp)
    assert len(bott) == 17
    assert abs(med - 4.355) < 0.001
    worst = bott.iloc[0]
    assert worst[C.COL_STATE] == "Minnesota"
    assert worst["avg_lead_days"] == 4.96


def test_region_performance_pinned(df):
    r = kpis.region_performance(df).set_index(C.COL_REGION)
    assert int(r.loc["Pacific", "volume"]) == 3253
    assert int(r.loc["Gulf", "volume"]) == 1620
    assert abs(r.loc["Pacific", "sales"] - 46_301.53) < 0.01


# ── Factory concentration ────────────────────────────────────────────────────

def test_factory_concentration_pinned(df):
    conc = analytics.factory_concentration(df)
    assert conc["factories"] == 5
    assert conc["top_n_share_pct"] == 96.6
    assert conc["top_n_names"] == ["Lot's O' Nuts", "Wicked Choccy's"]
    fp = analytics.factory_performance(df).set_index(C.COL_FACTORY)
    assert int(fp.loc["Lot's O' Nuts", "volume"]) == 5692
    assert float(fp.loc["Lot's O' Nuts", "volume_share_pct"]) == 55.8


def test_state_drilldown(df):
    d = analytics.state_drilldown(df, "Indiana")
    assert d["rows"] == 149
    assert d["avg_lead_days"] == 4.71
    assert len(d["routes"]) == 4
    # timeline: most recent 50 lines, all needed columns
    assert len(d["timeline"]) == 50
    assert C.COL_LEAD_RAW in d["timeline"].columns  # audit trail preserved
