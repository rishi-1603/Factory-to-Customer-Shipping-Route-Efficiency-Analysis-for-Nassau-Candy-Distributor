"""
test_theme_config.py — the dark theme must be configured, not just styled.

Regression (found 2026-10-14, reported by the project owner): the app's CSS
palette is a dark route-ops console, but --z-bg was only *defined* — nothing
applied it, and there was no .streamlit/config.toml. The page rendered white
while section titles/headings used light-on-dark colours, and the broken
chart-card wrapper divs rendered as empty dark bars.

This pins the fix: the Streamlit theme config must exist and match the app's
palette, so every native widget (sidebar, tabs, tables, filters) renders dark.
"""
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / ".streamlit" / "config.toml"

# The app's palette constants (dashboard/app.py)
BG = "#0B1220"
CARD = "#151E31"
TEXT = "#E8ECF4"
PRIMARY = "#388bfd"


def test_theme_config_exists():
    assert CONFIG.exists(), (
        ".streamlit/config.toml is missing — the app renders on a white page "
        "and its light-on-dark text becomes unreadable"
    )


def test_theme_config_is_dark_and_matches_palette():
    theme = tomllib.loads(CONFIG.read_text(encoding="utf-8"))["theme"]
    assert theme["base"] == "dark", "base must be dark for the dark console"
    assert theme["backgroundColor"].lower() == BG.lower()
    assert theme["secondaryBackgroundColor"].lower() == CARD.lower()
    assert theme["textColor"].lower() == TEXT.lower()
    assert theme["primaryColor"].lower() == PRIMARY.lower()


def test_no_broken_chart_card_wrappers():
    """chart-card divs cannot wrap Streamlit elements (they rendered as empty
    dark bars); charts are styled via [data-testid="stPlotlyChart"] instead."""
    app = (ROOT / "dashboard" / "app.py").read_text(encoding="utf-8")
    assert '<div class="chart-card">' not in app, (
        "broken chart-card wrapper divs are back — charts must be styled via "
        "the stPlotlyChart CSS rule, not split HTML blocks"
    )
    assert '[data-testid="stPlotlyChart"]' in app, (
        "the stPlotlyChart card styling rule is missing"
    )
