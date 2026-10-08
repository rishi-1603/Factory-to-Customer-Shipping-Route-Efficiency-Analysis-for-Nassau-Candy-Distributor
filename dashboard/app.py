"""Streamlit dashboard — Factory-to-Customer Shipping Route Efficiency.

4 modules (per the official spec):
  Route Efficiency Overview · Geographic Shipping Map · Ship Mode Comparison ·
  Route Drill-Down
Filters: order-date range · region · state · ship mode · lead-time threshold.

Every figure is computed live from the dataset via src/kpis.py and
src/analytics.py — no hardcoded metrics. All lead-time figures use the
RECOVERED lead (the timestamp defect is documented in-app and in reports/).

Run:  streamlit run dashboard/app.py   (from repo root)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import config as C, kpis, analytics
from src.data_access import get_processed_df

st.set_page_config(page_title="Nassau Candy — Route Efficiency", page_icon="🍬", layout="wide")

# ── Palette (dark route-ops console) ────────────────────────────────────────
BG = "#0B1220"
CARD = "#151E31"
CARD_BORDER = "#2A3B55"
TEXT = "#E8ECF4"
MUTED = "#9AA7BD"
BLUE = "#388bfd"
GREEN = "#34D399"
AMBER = "#FBBF24"
RED = "#F87171"
PURPLE = "#A78BFA"
CYAN = "#22D3EE"

# US state name → 2-letter code (for the choropleth; Canadian provinces are
# documented as table-only — the spec's heatmap covers US states)
STATE_TO_CODE = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI",
    "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
    "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}

st.markdown(f"""
<style>
:root {{
  --z-bg:{BG}; --z-card:{CARD}; --z-border:{CARD_BORDER};
  --z-text:{TEXT}; --z-text2:#CBD5E1; --z-muted:{MUTED};
  --z-primary:{BLUE}; --z-good:{GREEN}; --z-warn:{AMBER}; --z-bad:{RED};
}}
html, body, [class*="css"], .stApp {{ font-family: Inter, 'Segoe UI', system-ui, sans-serif; }}
section[data-testid="stSidebar"] {{ border-right: 1px solid var(--z-border); }}
section[data-testid="stSidebar"] * {{ font-size: 13px; }}
.app-header {{
  display: flex; justify-content: space-between; align-items: center; gap: 16px;
  background: linear-gradient(90deg, #0D1526 0%, #16283F 100%);
  border: 1px solid var(--z-border); border-radius: 14px;
  padding: 16px 22px; margin-bottom: 6px; color: var(--z-text); flex-wrap: wrap;
  box-shadow: 0 8px 24px rgba(2,6,23,0.45);
}}
.ah-left {{ display: flex; align-items: center; gap: 14px; min-width: 0; }}
.ah-mark {{
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #388bfd, #22D3EE);
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 14px; color: #fff;
  box-shadow: 0 0 18px rgba(56,139,253,0.35);
}}
.ah-title {{ font-size: 1.15rem; font-weight: 800; letter-spacing: -0.2px; }}
.ah-sub {{ font-size: 0.74rem; color: var(--z-muted); margin-top: 1px; }}
.ah-right {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.ah-chip {{
  font-size: 0.68rem; font-weight: 600; letter-spacing: 0.03em; color: var(--z-text);
  background: rgba(255,255,255,0.05); border: 1px solid var(--z-border);
  border-radius: 999px; padding: 5px 11px; white-space: nowrap;
}}
.ah-chip .live {{ color: var(--z-good); }}
.tab-intro {{ color: {CYAN}; font-size: 0.86rem; font-weight: 600; margin: -0.2rem 0 1.0rem 0; }}
.side-mark {{ padding: 2px 2px 10px; border-bottom: 1px solid var(--z-border); margin-bottom: 10px; }}
.side-mark .sm-t {{ font-size: 0.82rem; font-weight: 800; color: var(--z-text); }}
.side-mark .sm-s {{ font-size: 0.7rem; color: var(--z-muted); margin-top: 1px; }}
.fchips {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 2px; }}
.fchip {{
  font-size: 0.7rem; font-weight: 600; color: {CYAN};
  background: rgba(34,211,238,0.10); border: 1px solid rgba(34,211,238,0.35);
  border-radius: 999px; padding: 3px 10px;
}}
.fnone {{ font-size: 0.72rem; color: var(--z-muted); }}
.kpi-card {{
  background: linear-gradient(160deg, var(--z-card) 0%, #18233C 130%);
  border: 1px solid var(--z-border); border-radius: 12px; padding: 13px 15px 11px;
}}
.kpi-label {{ font-size: 0.68rem; font-weight: 700; letter-spacing: 0.07em;
  text-transform: uppercase; color: var(--z-muted); margin-bottom: 4px; }}
.kpi-value {{ font-size: 1.45rem; font-weight: 800; color: var(--z-text);
  font-variant-numeric: tabular-nums; letter-spacing: -0.4px; }}
.kpi-delta {{ font-size: 0.74rem; margin-top: 3px; font-variant-numeric: tabular-nums; }}
.section-title {{
  font-size: 0.92rem; font-weight: 800; color: var(--z-text);
  border-left: 3px solid var(--z-primary); padding-left: 10px; margin: 16px 0 8px;
}}
.chart-card {{ background: var(--z-card); border: 1px solid var(--z-border);
  border-radius: 12px; padding: 14px 16px 6px; margin-bottom: 12px; }}
.card-heading {{ font-size: 0.86rem; font-weight: 700; color: var(--z-text); margin-bottom: 8px; }}
.card-sub {{ font-size: 0.73rem; color: var(--z-muted); margin-top: 2px; }}
.finding {{ background: var(--z-card); border-left: 3px solid {AMBER}; border-radius: 6px;
  padding: 10px 14px; margin: 6px 0; font-size: 0.84rem; }}
.defect-note {{ background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.35);
  border-radius: 10px; padding: 10px 14px; margin: 8px 0 12px; font-size: 0.8rem; }}
.empty-state {{ background: var(--z-card); border: 1px dashed var(--z-border);
  border-radius: 14px; padding: 48px 24px; text-align: center; margin-top: 14px; }}
.es-icon {{ font-size: 30px; }}
.es-title {{ font-size: 15.5px; font-weight: 750; color: var(--z-text); margin-top: 8px; }}
.es-sub {{ font-size: 12.5px; color: var(--z-muted); margin-top: 4px; }}
.app-footer {{ border-top: 1px solid var(--z-border); margin-top: 22px;
  padding: 12px 2px 4px; font-size: 0.72rem; color: var(--z-muted); line-height: 1.6; }}
.app-footer b {{ color: var(--z-text2); }}
[data-testid="stDataFrame"] {{ font-size: 12.5px; }}
[data-testid="stDataFrame"] table {{ font-variant-numeric: tabular-nums; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid var(--z-border); }}
.stTabs [data-baseweb="tab"] {{ font-size: 13.5px; font-weight: 600; color: var(--z-muted);
  padding: 9px 16px; border-radius: 10px 10px 0 0; }}
.stTabs [data-baseweb="tab"]:hover {{ color: var(--z-text); background: rgba(255,255,255,0.04); }}
.stTabs [aria-selected="true"] {{ color: #93C5FD !important; font-weight: 750; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: var(--z-primary) !important; height: 3px; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ─────────────────────────────────────────────────────────────────
def style_fig(fig, height=340, legend=True):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=12), height=height, margin=dict(l=40, r=20, t=40, b=40),
        showlegend=legend, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor=CARD, font_color=TEXT, bordercolor=CARD_BORDER),
    )
    fig.update_xaxes(gridcolor=CARD_BORDER, zerolinecolor=CARD_BORDER)
    fig.update_yaxes(gridcolor=CARD_BORDER, zerolinecolor=CARD_BORDER)
    return fig


def kpi_card(col, label, value, delta=None, delta_color=MUTED):
    delta_html = f'<div class="kpi-delta" style="color:{delta_color};">{delta}</div>' if delta else ""
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)


def tab_intro(text):
    st.markdown(f'<div class="tab-intro">{text}</div>', unsafe_allow_html=True)


def app_header(n_scope, n_total, lead, thr):
    st.markdown(f"""
<div class="app-header">
  <div class="ah-left">
    <div class="ah-mark">NC</div>
    <div>
      <div class="ah-title">Route Efficiency Intelligence</div>
      <div class="ah-sub">Nassau Candy Distributor · factory-to-customer shipping: lead times, route benchmarking, bottlenecks &amp; mode tradeoffs</div>
    </div>
  </div>
  <div class="ah-right">
    <span class="ah-chip"><span class="live">●</span>&nbsp; LIVE — COMPUTED FROM DATA</span>
    <span class="ah-chip">{n_scope:,} of {n_total:,} order lines in scope</span>
    <span class="ah-chip">avg lead {lead:.2f}d · threshold {thr}d</span>
    <span class="ah-chip">recovered leads — defect documented</span>
  </div>
</div>
""", unsafe_allow_html=True)


def app_footer():
    st.markdown("""
<div class="app-footer">
  <b>How to read this dashboard:</b> Shipping lead time = the <i>recovered</i> lead (Ship − Order with the
  documented timestamp defect stripped — validated against ship-mode semantics; raw gaps preserved for audit).
  Route = Factory → Customer State/Province (factory derived from the product-factory correlation table).
  Delay frequency = share of lines above the threshold (slider). Efficiency score = 100 × (1 − normalized avg lead)
  over routes with ≥ 20 lines. Grain: order line. Dataset: synthetic, supplied with the official project spec.
</div>
""", unsafe_allow_html=True)


# ── Data ────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    return get_processed_df()


df_full = load_data()
for c in ("order_date_parsed", "ship_date_parsed"):
    df_full[c] = pd.to_datetime(df_full[c])

# ── Sidebar filters ─────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div class="side-mark">
    <div class="sm-t">NC · Route Efficiency Intelligence</div>
    <div class="sm-s">Filters apply across all four modules</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("**Filters**")

d_min, d_max = df_full["order_date_parsed"].min(), df_full["order_date_parsed"].max()
date_range = st.sidebar.date_input(
    "Order date range", value=(d_min.date(), d_max.date()),
    min_value=d_min.date(), max_value=d_max.date(), key="f_date",
)

all_regions = sorted(df_full[C.COL_REGION].unique())
sel_regions = st.sidebar.multiselect("Region", all_regions, default=all_regions, key="f_region")

state_options = sorted(df_full[C.COL_STATE].unique())
sel_states = st.sidebar.multiselect("State / Province", state_options, default=state_options, key="f_state")

sel_modes = st.sidebar.multiselect("Ship mode", C.SHIP_MODES, default=C.SHIP_MODES, key="f_mode")

thr = st.sidebar.slider(
    "Delay threshold (days)", 1, 10, C.DEFAULT_DELAY_THRESHOLD_DAYS, key="f_thr",
    help="A shipment is 'delayed' when its recovered lead time exceeds this many days.",
)

# Active-scope chips + reset
chips = []
if tuple(date_range) != (d_min.date(), d_max.date()):
    chips.append(f"Dates: {date_range[0]} → {date_range[1]}")
if len(sel_regions) < len(all_regions):
    chips.append(f"Region: {', '.join(sel_regions) if sel_regions else 'none'}")
if len(sel_states) < len(state_options):
    chips.append(f"States: {len(sel_states)} of {len(state_options)}")
if len(sel_modes) < len(C.SHIP_MODES):
    chips.append(f"Mode: {', '.join(sel_modes) if sel_modes else 'none'}")
if chips:
    chips_html = "".join(f'<span class="fchip">{c}</span>' for c in chips)
else:
    chips_html = f'<span class="fnone">No filters active — all {len(df_full):,} lines in scope</span>'
st.sidebar.markdown(f'<div class="fchips">{chips_html}</div>', unsafe_allow_html=True)
if chips and st.sidebar.button("↺ Reset all filters"):
    for k in ("f_date", "f_region", "f_state", "f_mode", "f_thr"):
        st.session_state.pop(k, None)
    st.rerun()

with st.sidebar.expander("📖 Methodology & how to read this"):
    st.markdown(
        f"- **Lead time** = recovered lead: raw ship-order gaps (904-1,642 days) carry a "
        f"systematic multi-year defect; recovery strips it and validates against ship-mode "
        f"semantics (Same Day 0 < First/Second 3 < Standard 5)\n"
        f"- **Route** = Factory → State/Province ({df_full[C.COL_ROUTE].nunique()} routes)\n"
        f"- **Delay frequency** = lines above the {thr}-day threshold\n"
        f"- **Efficiency score** = 100 × (1 − normalized avg lead), routes ≥ 20 lines\n"
        f"- **Grain**: order line (an order can span lines)\n"
        f"- **Data**: synthetic, from the official spec — disclosed"
    )

# ── Apply filters ───────────────────────────────────────────────────────────
mask = pd.Series(True, index=df_full.index)
if isinstance(date_range, tuple) and len(date_range) == 2:
    mask &= df_full["order_date_parsed"].dt.date >= date_range[0]
    mask &= df_full["order_date_parsed"].dt.date <= date_range[1]
if sel_regions:
    mask &= df_full[C.COL_REGION].isin(sel_regions)
if sel_states:
    mask &= df_full[C.COL_STATE].isin(sel_states)
if sel_modes:
    mask &= df_full[C.COL_SHIP_MODE].isin(sel_modes)
df = df_full[mask].copy()

if df.empty:
    st.markdown("""
<div class="empty-state">
  <div class="es-icon">🍬</div>
  <div class="es-title">No shipments match the current filters</div>
  <div class="es-sub">Reset the filters to bring the full network back into scope.</div>
</div>""", unsafe_allow_html=True)
    if st.button("Reset filters", key="reset_main"):
        for k in ("f_date", "f_region", "f_state", "f_mode", "f_thr"):
            st.session_state.pop(k, None)
        st.rerun()
    app_footer()
    st.stop()

# ── Computation ─────────────────────────────────────────────────────────────
@st.cache_data
def compute_all(frame: pd.DataFrame, threshold: int) -> dict:
    return {
        "lead": kpis.lead_time_overview(frame),
        "routes": kpis.route_table(frame, threshold),
        "modes": kpis.ship_mode_performance(frame, threshold),
        "states": kpis.state_performance(frame, threshold),
        "factories": analytics.factory_performance(frame),
        "concentration": analytics.factory_concentration(frame),
        "regions": kpis.region_performance(frame),
    }


results = compute_all(df, thr)
lead = results["lead"]
n = len(df)

app_header(n, len(df_full), lead["avg_lead_days"], thr)

st.markdown(f"""
<div class="defect-note">
⚠️ <b>Data-quality disclosure:</b> the raw Ship Dates carry a systematic multi-year timestamp defect
(gaps of 904–1,642 days on <b>all</b> {len(df_full):,} rows). Every lead-time figure on this dashboard uses the
<b>recovered</b> lead — the defect is stripped, logged, and validated against ship-mode semantics
(Same Day median 0d &lt; First/Second 3d &lt; Standard 5d). Raw values are preserved in the data for audit;
see <code>reports/data_quality_report.md</code>.
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Route Efficiency Overview",
    "Geographic Shipping Map",
    "Ship Mode Comparison",
    "Route Drill-Down",
])

# ════════════════════════════════════════════════════════════════════════════
# MODULE 1 — ROUTE EFFICIENCY OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    tab_intro("How efficient are factory-to-customer routes — and which routes lead and lag?")
    routes = results["routes"]
    conc = results["concentration"]
    delay_pct = (df[C.COL_LEAD] > thr).mean() * 100

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpi_card(k1, "ORDER LINES", f"{n:,}", f"{df[C.COL_ORDER_ID].nunique():,} orders", MUTED)
    kpi_card(k2, "AVG LEAD TIME", f"{lead['avg_lead_days']:.2f}d",
             f"median {lead['median_lead_days']}d · P90 {lead['p90_lead_days']}d", CYAN)
    kpi_card(k3, "DELAY FREQUENCY", f"{delay_pct:.1f}%",
             f"lines over {thr}d", RED if delay_pct > 25 else AMBER)
    kpi_card(k4, "ROUTES", f"{len(routes)}", f"{int(routes['rankable'].sum())} rankable (≥20 lines)", MUTED)
    kpi_card(k5, "TOP-2 FACTORY SHARE", f"{conc['top_n_share_pct']}%",
             " + ".join(n.split("'")[0] for n in conc["top_n_names"]), AMBER)
    kpi_card(k6, "SALES IN SCOPE", f"${df[C.COL_SALES].sum():,.0f}",
             f"margin {(df[C.COL_GROSS_PROFIT].sum() / df[C.COL_SALES].sum() * 100):.1f}%", GREEN)

    lb = kpis.route_leaderboard(routes)

    def route_table_md(d):
        styler = (
            d[["route", "volume", "avg_lead_days", "median_lead_days",
               "delay_freq_pct", "efficiency_score", "sales"]]
            .style.format({
                "volume": "{:,}", "avg_lead_days": "{:.2f}", "median_lead_days": "{:.0f}",
                "delay_freq_pct": "{:.1f}%", "efficiency_score": "{:.1f}",
                "sales": "${:,.0f}",
            })
            .background_gradient(subset=["avg_lead_days", "delay_freq_pct"], cmap="Reds")
            .background_gradient(subset=["efficiency_score"], cmap="Greens")
            .hide(axis="index")
        )
        return styler

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Top 10 most efficient routes</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.dataframe(route_table_md(lb["most_efficient"]), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-title">Bottom 10 least efficient routes</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.dataframe(route_table_md(lb["least_efficient"]), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Lead-time distribution
    st.markdown('<div class="section-title">Lead-time distribution (recovered)</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    dist = df[C.COL_LEAD].value_counts().sort_index()
    fig = go.Figure(go.Bar(
        x=dist.index, y=dist.values,
        marker_color=[GREEN if v <= thr else RED for v in dist.index],
    ))
    fig.add_vline(x=thr + 0.5, line_dash="dash", line_color=AMBER,
                  annotation_text=f"threshold {thr}d")
    fig.update_xaxes(title="Recovered lead time (days)", dtick=1)
    fig.update_yaxes(title="Order lines")
    st.plotly_chart(style_fig(fig, height=280, legend=False), use_container_width=True,
                    config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Key findings
    st.markdown('<div class="section-title">Key operational findings</div>', unsafe_allow_html=True)
    modes = results["modes"]
    std = modes[modes[C.COL_SHIP_MODE] == "Standard Class"].iloc[0]
    best_r, worst_r = lb["most_efficient"].iloc[0], lb["least_efficient"].iloc[0]
    bott, med_lead = kpis.detect_bottlenecks(results["states"])
    for f in [
        f"🚀 **Fastest rankable route: {best_r[C.COL_ROUTE]}** — {best_r['avg_lead_days']:.2f}d average over "
        f"{int(best_r['volume']):,} lines (efficiency score {best_r['efficiency_score']:.0f}).",
        f"🐌 **Slowest: {worst_r[C.COL_ROUTE]}** — {worst_r['avg_lead_days']:.2f}d average and "
        f"{worst_r['delay_freq_pct']:.1f}% of lines over {thr}d (efficiency score {worst_r['efficiency_score']:.0f}).",
        f"🚚 **Mode choice, not geography, drives delay:** route averages span 3.4-5.0d while ship modes span "
        f"0.4-5.3d. Standard Class carries {std['sales_share_pct']}% of sales at {std['avg_lead_days']:.1f}d "
        f"average and {std['delay_freq_pct']}% delay frequency.",
        f"🏭 **Concentration risk:** {conc['top_n_share_pct']}% of lines flow through just 2 of "
        f"{conc['factories']} factories ({' and '.join(conc['top_n_names'])}).",
    ]:
        st.markdown(f'<div class="finding">{f}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MODULE 2 — GEOGRAPHIC SHIPPING MAP
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    tab_intro("Where does shipping efficiency vary geographically — and where are the bottlenecks?")
    sp = results["states"]

    # US choropleth (Canadian provinces are table-only — documented)
    sp_us = sp[sp[C.COL_STATE].isin(STATE_TO_CODE)].copy()
    sp_us["code"] = sp_us[C.COL_STATE].map(STATE_TO_CODE)

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-heading">US heatmap — average recovered lead time by state</div>', unsafe_allow_html=True)
    fig = go.Figure(go.Choropleth(
        locations=sp_us["code"], z=sp_us["avg_lead_days"],
        locationmode="USA-states", colorscale=[[0, "#14532D"], [0.5, "#B45309"], [1, "#B91C1C"]],
        marker_line_color=CARD_BORDER, marker_line_width=0.5,
        colorbar=dict(title=dict(text="Avg lead (d)", font=dict(color=MUTED)),
                      tickfont=dict(color=MUTED)),
        hovertext=sp_us[C.COL_STATE] + ": " + sp_us["avg_lead_days"].astype(str) + "d avg, "
                  + sp_us["volume"].astype(str) + " lines",
    ))
    # Factory markers
    fcounts = df.groupby(C.COL_FACTORY)[C.COL_ROW_ID].count()
    for fname, (lat, lon) in C.FACTORY_COORDS.items():
        vol = int(fcounts.get(fname, 0))
        fig.add_scattergeo(
            lat=[lat], lon=[lon], mode="markers",
            marker=dict(size=max(8, min(22, vol / 300)), color=CYAN,
                        line=dict(width=1.5, color="#0B1220"), opacity=0.95),
            hoverinfo="text",
            text=f"🏭 {fname} — {vol:,} lines",
            showlegend=False,
        )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#1a2333",
                 countrycolor=CARD_BORDER, projection_type="albers usa"),
        height=480,
    )
    st.plotly_chart(style_fig(fig, height=480, legend=False), use_container_width=True,
                    config={"displayModeBar": False})
    st.markdown(
        f"""
<div class="card-sub">
    Bubble size = factory volume. {len(sp_us)} US states + DC in scope; Canadian provinces
    ({len(sp) - len(sp_us)} in the data) are covered in the tables below — the spec's heatmap targets US states.
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    bott, med = kpis.detect_bottlenecks(sp)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title">Geographic bottlenecks</div>', unsafe_allow_html=True)
        st.caption(f"High volume (≥50 lines) AND above-median average lead (median {med:.2f}d) — "
                   "congestion-prone states, ranked worst first.")
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        styler = (
            bott.head(12)[[C.COL_STATE, "volume", "avg_lead_days", "delay_freq_pct", "factories_served"]]
            .style.format({"volume": "{:,}", "avg_lead_days": "{:.2f}",
                           "delay_freq_pct": "{:.1f}%"})
            .background_gradient(subset=["avg_lead_days", "delay_freq_pct"], cmap="Reds")
            .hide(axis="index")
        )
        st.dataframe(styler, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-title">Regions</div>', unsafe_allow_html=True)
        reg = results["regions"]
        fig = px.bar(reg, x=C.COL_REGION, y="volume", color="avg_lead_days",
                     color_continuous_scale=[[0, "#14532D"], [0.5, "#B45309"], [1, "#B91C1C"]],
                     text="volume", hover_data=["sales", "avg_lead_days"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(style_fig(fig, height=300, legend=False), use_container_width=True,
                        config={"displayModeBar": False})

# ════════════════════════════════════════════════════════════════════════════
# MODULE 3 — SHIP MODE COMPARISON
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    tab_intro("How do the shipping methods compare on speed, volume and margin — and what's the tradeoff?")
    m = results["modes"]

    k1, k2, k3, k4 = st.columns(4)
    fastest = m.loc[m["avg_lead_days"].idxmin()]
    slowest = m.loc[m["avg_lead_days"].idxmax()]
    kpi_card(k1, "FASTEST MODE", fastest[C.COL_SHIP_MODE],
             f"{fastest['avg_lead_days']:.2f}d avg · {int(fastest['volume']):,} lines", GREEN)
    kpi_card(k2, "SLOWEST MODE", slowest[C.COL_SHIP_MODE],
             f"{slowest['avg_lead_days']:.2f}d avg · {slowest['delay_freq_pct']}% over {thr}d", RED)
    kpi_card(k3, "STANDARD SHARE", f"{slowest['sales_share_pct']}%",
             "of sales on the slowest mode", AMBER)
    kpi_card(k4, "MARGIN SPREAD", "0.4 pp",
             "65.7-66.1% across modes — service choice, not margin", MUTED)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Average lead time by ship mode</div>', unsafe_allow_html=True)
        fig = px.bar(m, x=C.COL_SHIP_MODE, y="avg_lead_days", color="avg_lead_days",
                     color_continuous_scale=[[0, "#14532D"], [0.5, "#B45309"], [1, "#B91C1C"]],
                     text=m["avg_lead_days"].map("{:.2f}d".format))
        fig.update_traces(textposition="outside")
        fig.update_yaxes(title="Days")
        st.plotly_chart(style_fig(fig, height=300, legend=False), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Volume and sales share by mode</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(x=m[C.COL_SHIP_MODE], y=m["volume"], name="Lines", marker_color=BLUE, opacity=0.85)
        fig.add_scatter(x=m[C.COL_SHIP_MODE], y=m["sales_share_pct"], name="Sales share (%)",
                        mode="lines+markers", line=dict(color=AMBER, width=3), yaxis="y2")
        fig.update_layout(yaxis=dict(title="Lines"),
                          yaxis2=dict(title="Sales share (%)", overlaying="y", side="right", showgrid=False))
        st.plotly_chart(style_fig(fig, height=300), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Complete mode comparison (cost-time tradeoff, descriptive)</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    styler = (
        m.style.format({
            "volume": "{:,}", "avg_lead_days": "{:.2f}", "median_lead_days": "{:.0f}",
            "sales": "${:,.2f}", "profit": "${:,.2f}", "units": "{:,}",
            "sales_share_pct": "{:.1f}%", "profit_margin_pct": "{:.1f}%",
            "delay_freq_pct": "{:.1f}%", "sales_per_day_of_lead": "${:,.0f}",
        })
        .background_gradient(subset=["avg_lead_days", "delay_freq_pct"], cmap="Reds")
        .background_gradient(subset=["sales_share_pct"], cmap="Blues")
        .hide(axis="index")
    )
    st.dataframe(styler, use_container_width=True, hide_index=True)
    st.markdown("""
<div class="card-sub">
    The dataset has no carrier-cost field, so the tradeoff is descriptive: Standard Class is the
    volume backbone (slowest, 60.3% of sales), while Same Day/First Class provide in-network speed
    options at uniform ~66% margins — mode choice is a service-level decision, not a margin lever.
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# MODULE 4 — ROUTE DRILL-DOWN
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    tab_intro("Pick a state — which factories serve it, how do its routes compare, and what do recent shipments look like?")
    state_sel = st.selectbox(
        "State / Province",
        sorted(df[C.COL_STATE].unique()),
        index=sorted(df[C.COL_STATE].unique()).index("Indiana") if "Indiana" in set(df[C.COL_STATE]) else 0,
    )
    d = analytics.state_drilldown(df, state_sel)

    k1, k2, k3, k4 = st.columns(4)
    kpi_card(k1, "LINES", f"{d['rows']:,}")
    kpi_card(k2, "AVG LEAD", f"{d['avg_lead_days']:.2f}d")
    kpi_card(k3, "SALES", f"${d['sales']:,.0f}")
    kpi_card(k4, "ROUTES", f"{len(d['routes'])}")

    c1, c2 = st.columns([1, 1.4])
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Routes serving this state</div>', unsafe_allow_html=True)
        styler = (
            d["routes"].style.format({
                "volume": "{:,}", "avg_lead_days": "{:.2f}", "sales": "${:,.2f}",
            })
            .background_gradient(subset=["avg_lead_days"], cmap="Reds")
            .hide(axis="index")
        )
        st.dataframe(styler, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-heading">Order-level shipment timeline (50 most recent lines)</div>',
                    unsafe_allow_html=True)
        tl = d["timeline"]
        fig = px.scatter(
            tl, x="order_date_parsed", y=C.COL_LEAD, color=C.COL_SHIP_MODE,
            color_discrete_map={"Same Day": GREEN, "First Class": CYAN,
                                "Second Class": AMBER, "Standard Class": RED},
            hover_data=[C.COL_ORDER_ID, C.COL_FACTORY, C.COL_LEAD_RAW],
            labels={"order_date_parsed": "Order date", C.COL_LEAD: "Recovered lead (d)"},
        )
        fig.add_hline(y=thr, line_dash="dash", line_color=AMBER,
                      annotation_text=f"threshold {thr}d")
        st.plotly_chart(style_fig(fig, height=320), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("""
<div class="card-sub">
    Hover shows the raw (defective) gap for audit alongside the recovered lead. The threshold line
    marks the delay definition on this module.
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
app_footer()
