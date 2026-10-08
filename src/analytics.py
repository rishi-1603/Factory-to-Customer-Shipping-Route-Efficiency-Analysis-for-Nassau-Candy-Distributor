"""Diagnostic analytics: factory concentration, timelines, drill-down helpers."""
from __future__ import annotations

import pandas as pd

from . import config as C


def factory_performance(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(C.COL_FACTORY).agg(
        volume=(C.COL_ROW_ID, "count"),
        avg_lead_days=(C.COL_LEAD, "mean"),
        sales=(C.COL_SALES, "sum"),
        profit=(C.COL_GROSS_PROFIT, "sum"),
        products=(C.COL_PRODUCT_NAME, "nunique"),
        states_served=(C.COL_STATE, "nunique"),
    ).reset_index()
    g["avg_lead_days"] = g["avg_lead_days"].round(2)
    g["volume_share_pct"] = (g["volume"] / g["volume"].sum() * 100).round(1)
    g["profit_margin_pct"] = (g["profit"] / g["sales"] * 100).round(1)
    return g.sort_values("volume", ascending=False).reset_index(drop=True)


def state_drilldown(df: pd.DataFrame, state: str) -> dict:
    """Everything about one state: routes, factories, recent order timeline."""
    sub = df[df[C.COL_STATE] == state]
    if not len(sub):
        return {"state": state, "rows": 0}
    by_route = sub.groupby(C.COL_ROUTE).agg(
        volume=(C.COL_ROW_ID, "count"),
        avg_lead_days=(C.COL_LEAD, "mean"),
        sales=(C.COL_SALES, "sum"),
    ).reset_index().sort_values("avg_lead_days")
    by_route["avg_lead_days"] = by_route["avg_lead_days"].round(2)
    by_mode = sub.groupby(C.COL_SHIP_MODE)[C.COL_LEAD].mean().round(2)
    timeline = sub.sort_values("order_date_parsed").tail(50)
    return {
        "state": state,
        "rows": int(len(sub)),
        "routes": by_route,
        "by_mode": by_mode,
        "timeline": timeline[[
            C.COL_ORDER_ID, "order_date_parsed", "ship_date_parsed",
            C.COL_LEAD, C.COL_LEAD_RAW, C.COL_SHIP_MODE, C.COL_FACTORY,
            C.COL_PRODUCT_NAME, C.COL_SALES,
        ]],
        "avg_lead_days": round(float(sub[C.COL_LEAD].mean()), 2),
        "sales": float(sub[C.COL_SALES].sum()),
    }


def factory_concentration(df: pd.DataFrame, top_n: int = 2) -> dict:
    """The concentration headline (e.g. 2 of 5 factories = 96.6% of lines)."""
    counts = df[C.COL_FACTORY].value_counts()
    share = counts.head(top_n).sum() / len(df) * 100
    return {
        "factories": int(counts.size),
        "top_n": top_n,
        "top_n_names": counts.head(top_n).index.tolist(),
        "top_n_share_pct": round(float(share), 1),
    }
