"""KPI engine — every dashboard number comes from here (spec KPIs 1-5)."""
from __future__ import annotations

import pandas as pd

from . import config as C


# ── KPI 1: Shipping Lead Time (recovered) ───────────────────────────────────

def lead_time_overview(df: pd.DataFrame) -> dict:
    lead = df[C.COL_LEAD]
    return {
        "shipments": int(len(df)),
        "avg_lead_days": round(float(lead.mean()), 2),
        "median_lead_days": int(lead.median()),
        "p90_lead_days": int(lead.quantile(0.9)),
        "min_lead_days": int(lead.min()),
        "max_lead_days": int(lead.max()),
        "raw_gap_min_days": int(df[C.COL_LEAD_RAW].min()),
        "raw_gap_max_days": int(df[C.COL_LEAD_RAW].max()),
    }


# ── KPI 2/3: Average Lead Time + Route Volume (route-level aggregation) ─────

def route_table(df: pd.DataFrame, threshold_days: int | None = None) -> pd.DataFrame:
    """One row per route (Factory → State/Province): volume, lead stats,
    delay frequency (KPI 4) and efficiency score (KPI 5)."""
    threshold = C.DEFAULT_DELAY_THRESHOLD_DAYS if threshold_days is None else threshold_days
    g = df.groupby(C.COL_ROUTE).agg(
        factory=(C.COL_FACTORY, "first"),
        state=(C.COL_STATE, "first"),
        volume=(C.COL_ROW_ID, "count"),
        avg_lead_days=(C.COL_LEAD, "mean"),
        median_lead_days=(C.COL_LEAD, "median"),
        p90_lead_days=(C.COL_LEAD, lambda x: float(x.quantile(0.9))),
        lead_std=(C.COL_LEAD, "std"),
        sales=(C.COL_SALES, "sum"),
        profit=(C.COL_GROSS_PROFIT, "sum"),
    ).reset_index()
    g["avg_lead_days"] = g["avg_lead_days"].round(2)
    g["p90_lead_days"] = g["p90_lead_days"].round(1)
    g["lead_std"] = g["lead_std"].fillna(0.0).round(2)

    # KPI 4 — delay frequency: % of the route's lines above the threshold
    delayed = df.assign(d=df[C.COL_LEAD] > threshold).groupby(C.COL_ROUTE)["d"].mean() * 100
    g["delay_freq_pct"] = g[C.COL_ROUTE].map(delayed).round(1)

    # KPI 5 — Route Efficiency Score: normalized lead-time performance.
    # Scored ONLY on routes with >= MIN_ROUTE_VOLUME_FOR_RANKING lines
    # (small-sample routes keep their raw stats but are excluded from the
    # min-max normalization — documented in docs/kpi_dictionary.md).
    rankable = g["volume"] >= C.MIN_ROUTE_VOLUME_FOR_RANKING
    lo = g.loc[rankable, "avg_lead_days"].min()
    hi = g.loc[rankable, "avg_lead_days"].max()
    span = (hi - lo) if hi > lo else 1.0
    g["efficiency_score"] = None
    g.loc[rankable, "efficiency_score"] = (
        (1 - (g.loc[rankable, "avg_lead_days"] - lo) / span) * 100
    ).round(1)
    g["rankable"] = rankable
    return g.sort_values("avg_lead_days").reset_index(drop=True)


# ── Route leaderboard (spec: top 10 most / least efficient) ─────────────────

def route_leaderboard(routes: pd.DataFrame, top_n: int = 10) -> dict:
    rankable = routes[routes["rankable"]].sort_values("efficiency_score", ascending=False)
    return {
        "most_efficient": rankable.head(top_n),
        "least_efficient": rankable.tail(top_n).iloc[::-1],
    }


# ── Ship Mode Performance (spec: compare efficiency by shipping method) ─────

def ship_mode_performance(df: pd.DataFrame, threshold_days: int | None = None) -> pd.DataFrame:
    threshold = C.DEFAULT_DELAY_THRESHOLD_DAYS if threshold_days is None else threshold_days
    g = df.groupby(C.COL_SHIP_MODE).agg(
        volume=(C.COL_ROW_ID, "count"),
        avg_lead_days=(C.COL_LEAD, "mean"),
        median_lead_days=(C.COL_LEAD, "median"),
        sales=(C.COL_SALES, "sum"),
        profit=(C.COL_GROSS_PROFIT, "sum"),
        units=(C.COL_UNITS, "sum"),
    ).reset_index()
    g["avg_lead_days"] = g["avg_lead_days"].round(2)
    g["sales_share_pct"] = (g["sales"] / g["sales"].sum() * 100).round(1)
    g["profit_margin_pct"] = (g["profit"] / g["sales"] * 100).round(1)
    delayed = df.assign(d=df[C.COL_LEAD] > threshold).groupby(C.COL_SHIP_MODE)["d"].mean() * 100
    g["delay_freq_pct"] = g[C.COL_SHIP_MODE].map(delayed).round(1)
    # Cost-time tradeoff (descriptive, per the spec)
    g["sales_per_day_of_lead"] = (g["sales"] / g["avg_lead_days"]).round(0)
    return g.set_index(C.COL_SHIP_MODE).reindex(C.SHIP_MODES).reset_index()


# ── Geographic bottleneck analysis (spec) ────────────────────────────────────

def state_performance(df: pd.DataFrame, threshold_days: int | None = None) -> pd.DataFrame:
    """State-level aggregation for the heatmap + bottleneck detection."""
    threshold = C.DEFAULT_DELAY_THRESHOLD_DAYS if threshold_days is None else threshold_days
    g = df.groupby(C.COL_STATE).agg(
        volume=(C.COL_ROW_ID, "count"),
        avg_lead_days=(C.COL_LEAD, "mean"),
        sales=(C.COL_SALES, "sum"),
        factories_served=(C.COL_FACTORY, "nunique"),
        routes=(C.COL_ROUTE, "nunique"),
    ).reset_index()
    g["avg_lead_days"] = g["avg_lead_days"].round(2)
    delayed = df.assign(d=df[C.COL_LEAD] > threshold).groupby(C.COL_STATE)["d"].mean() * 100
    g["delay_freq_pct"] = g[C.COL_STATE].map(delayed).round(1)
    return g.sort_values("avg_lead_days", ascending=False).reset_index(drop=True)


def region_performance(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(C.COL_REGION).agg(
        volume=(C.COL_ROW_ID, "count"),
        avg_lead_days=(C.COL_LEAD, "mean"),
        sales=(C.COL_SALES, "sum"),
        profit=(C.COL_GROSS_PROFIT, "sum"),
        states=(C.COL_STATE, "nunique"),
    ).reset_index()
    g["avg_lead_days"] = g["avg_lead_days"].round(2)
    g["profit_margin_pct"] = (g["profit"] / g["sales"] * 100).round(1)
    return g.sort_values("volume", ascending=False).reset_index(drop=True)


def detect_bottlenecks(state_perf: pd.DataFrame, min_volume: int = 50) -> pd.DataFrame:
    """Bottleneck = high average lead AND meaningful volume (the spec's
    'high shipment volume + poor performance' condition)."""
    cands = state_perf[state_perf["volume"] >= min_volume].copy()
    med = cands["avg_lead_days"].median()
    out = cands[cands["avg_lead_days"] > med].sort_values("avg_lead_days", ascending=False)
    return out, float(med)
