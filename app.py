import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import base64 as _b64

def _get_logo_b64():
    _logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(_logo_path):
        with open(_logo_path, "rb") as f:
            return _b64.b64encode(f.read()).decode()
    return None

_favicon_b64 = _get_logo_b64()
_favicon = "data:image/png;base64,{}".format(_favicon_b64) if _favicon_b64 else "🏢"

st.set_page_config(
    page_title="PATTON",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

try:
    from utils.style import inject_css, kpi, tr, score_bar, score_color, LOGO_B64
except Exception as e:
    st.error("Import error: {}".format(e))
    st.stop()

# ── Splash Screen ─────────────────────────────────────────
if "splash_done" not in st.session_state:
    st.session_state["splash_done"] = False

if not st.session_state["splash_done"]:
    # Dark full-screen overlay via fixed-position div
    logo_splash = ""
    if LOGO_B64:
        logo_splash = '<img src="data:image/png;base64,{}" style="height:140px;">'.format(LOGO_B64)

    st.markdown(
        '<div id="splash-overlay" style="'
        'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999999;'
        'background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0f172a 100%);'
        'display:flex;flex-direction:column;align-items:center;justify-content:center;'
        'text-align:center;">'
        '{logo}'
        '<div style="font-size:2.8rem;font-weight:900;color:#ffffff;letter-spacing:-1px;margin-top:1.5rem;">PATTON</div>'
        '<div style="width:60px;height:3px;background:linear-gradient(90deg,#2563eb,#d4a853);border-radius:2px;margin:1.2rem auto;"></div>'
        '<div style="font-size:0.75rem;color:#94a3b8;letter-spacing:4px;text-transform:uppercase;font-weight:600;">Real Estate Intelligence</div>'
        '</div>'.format(logo=logo_splash),
        unsafe_allow_html=True,
    )

    # Password + ENTER
    st.markdown('<div style="height:30vh;"></div>', unsafe_allow_html=True)
    _c1, _c2, _c3 = st.columns([2, 1, 2])
    with _c2:
        pwd = st.text_input("Password", type="password", placeholder="Enter password", key="splash_pwd", label_visibility="collapsed")
        if st.button("ENTER", key="splash_enter", type="primary", use_container_width=True):
            if pwd == "pattonre.com":
                st.session_state["splash_done"] = True
                st.rerun()
            else:
                st.error("Incorrect password")
    st.stop()

inject_css()

# Top bar: theme toggle + news
_tb_spacer, _tb_news, _tb_theme = st.columns([0.8, 0.1, 0.1])
with _tb_news:
    if st.button("News", key="top_news"):
        st.session_state["app_mode"] = "news"
        st.rerun()
with _tb_theme:
    theme = st.session_state.get("theme", "light")
    icon_label = "\U0001f319" if theme == "light" else "\u2600\ufe0f"
    if st.button(icon_label, key="theme_btn"):
        st.session_state["theme"] = "dark" if theme == "light" else "light"
        st.rerun()

# ── App Mode Routing ──────────────────────────────────────
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = "home"

if st.session_state["app_mode"] == "office":
    from page_office import render_office_page
    render_office_page()
    st.stop()

if st.session_state["app_mode"] == "abstract":
    from page_abstract import render_abstract_page
    render_abstract_page()
    st.stop()

if st.session_state["app_mode"] == "proposal":
    from page_proposal import render_proposal_page
    render_proposal_page()
    st.stop()

if st.session_state["app_mode"] == "projects":
    from page_projects import render_projects_page
    render_projects_page()
    st.stop()

if st.session_state["app_mode"] == "buildings":
    from page_buildings import render_buildings_page
    render_buildings_page()
    st.stop()

if st.session_state["app_mode"] == "brokers":
    from page_brokers import render_brokers_page
    render_brokers_page()
    st.stop()

if st.session_state["app_mode"] == "tenants":
    from page_tenants import render_tenants_page
    render_tenants_page()
    st.stop()

if st.session_state["app_mode"] == "news":
    from page_news import render_news_page
    render_news_page()
    st.stop()

if st.session_state["app_mode"] == "calendar":
    from page_calendar import render_calendar_page
    render_calendar_page()
    st.stop()

if st.session_state["app_mode"] == "rent":
    from page_rent import render_rent_page
    render_rent_page()
    st.stop()

# ── HOME PAGE ─────────────────────────────────────────────
if st.session_state["app_mode"] == "home":
    st.markdown(
        '<style>'
        'section[data-testid="stSidebar"] { display: none !important; }'
        '.block-container { max-width: 960px !important; padding-top: 0 !important; }'
        '</style>',
        unsafe_allow_html=True,
    )

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:140px;filter:drop-shadow(0 8px 32px rgba(0,0,0,0.15));">'.format(LOGO_B64)

    st.markdown(
        '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:30vh;text-align:center;padding-top:4vh;">'
        '{logo}'
        '<h1 style="font-size:2.6rem;font-weight:900;color:var(--text-primary);letter-spacing:-1.5px;margin:1rem 0 0.3rem;">PATTON</h1>'
        '<div style="width:50px;height:3px;background:linear-gradient(90deg, var(--accent), var(--gold));border-radius:2px;margin:0 auto;"></div>'
        '<div style="font-size:0.72rem;color:var(--text-muted);letter-spacing:3px;text-transform:uppercase;margin-top:0.8rem;font-weight:600;">Real Estate Intelligence</div>'
        '<div style="font-size:0.82rem;color:var(--text-tertiary);margin-top:0.4rem;">Patton Commercial Real Estate &mdash; Miami-Dade County</div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)

    CARD_STYLE = (
        'text-align:center;padding:2rem 1.5rem;min-height:220px;'
        'border:1px solid var(--border);transition:all 0.25s;cursor:pointer;'
        'background:var(--bg-card);'
    )
    ICON_STYLE = (
        'width:52px;height:52px;border-radius:14px;display:flex;align-items:center;'
        'justify-content:center;margin:0 auto 0.8rem;font-size:1.5rem;'
    )

    # Row 1
    lc, rc = st.columns(2, gap="large")
    with lc:
        st.markdown(
            '<div class="card" style="{cs}">'
            '<div style="{ic}background:var(--accent-soft);border:1px solid var(--accent-border);">&#x1F50D;</div>'
            '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);margin-bottom:0.5rem;">Property Search</div>'
            '<p style="font-size:0.76rem;color:var(--text-tertiary);line-height:1.65;margin:0 0 0.8rem;">Analyze any Miami-Dade address: zoning, market comps, valuation, risk, AI recommendations.</p>'
            '<div style="display:flex;gap:0.3rem;flex-wrap:wrap;justify-content:center;">'
            '<span class="badge badge-blue">12 Tabs</span>'
            '<span class="badge badge-green">AI Scoring</span>'
            '</div></div>'.format(cs=CARD_STYLE, ic=ICON_STYLE),
            unsafe_allow_html=True,
        )
        if st.button("PROPERTY SEARCH", use_container_width=True, key="btn_property", type="primary"):
            st.session_state["app_mode"] = "property"
            st.rerun()

    with rc:
        st.markdown(
            '<div class="card" style="{cs}">'
            '<div style="{ic}background:var(--green-soft);border:1px solid var(--green-border);">&#x1F3E2;</div>'
            '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);margin-bottom:0.5rem;">Office Suite Finder</div>'
            '<p style="font-size:0.76rem;color:var(--text-tertiary);line-height:1.65;margin:0 0 0.8rem;">Set budget, pick size, choose building with amenities, find the perfect suite with floor plans.</p>'
            '<div style="display:flex;gap:0.3rem;flex-wrap:wrap;justify-content:center;">'
            '<span class="badge badge-blue">3 Buildings</span>'
            '<span class="badge badge-green">16 Suites</span>'
            '</div></div>'.format(cs=CARD_STYLE, ic=ICON_STYLE),
            unsafe_allow_html=True,
        )
        if st.button("OFFICE SUITE FINDER", use_container_width=True, key="btn_office", type="primary"):
            st.session_state["app_mode"] = "office"
            st.rerun()

    st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

    # Row 2
    lc2, rc2 = st.columns(2, gap="large")
    with lc2:
        st.markdown(
            '<div class="card" style="{cs}">'
            '<div style="{ic}background:var(--amber-soft);border:1px solid var(--amber-border);">&#x1F4C4;</div>'
            '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);margin-bottom:0.5rem;">Lease Abstract</div>'
            '<p style="font-size:0.76rem;color:var(--text-tertiary);line-height:1.65;margin:0 0 0.8rem;">Upload a scanned lease PDF and generate a structured abstract with all key terms extracted.</p>'
            '<div style="display:flex;gap:0.3rem;flex-wrap:wrap;justify-content:center;">'
            '<span class="badge badge-amber">PDF Upload</span>'
            '<span class="badge badge-blue">Auto-Extract</span>'
            '</div></div>'.format(cs=CARD_STYLE, ic=ICON_STYLE),
            unsafe_allow_html=True,
        )
        if st.button("LEASE ABSTRACT", use_container_width=True, key="btn_abstract", type="primary"):
            st.session_state["app_mode"] = "abstract"
            st.rerun()

    with rc2:
        st.markdown(
            '<div class="card" style="{cs}">'
            '<div style="{ic}background:var(--red-soft);border:1px solid var(--red-border);">&#x1F4DD;</div>'
            '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);margin-bottom:0.5rem;">Lease Proposal</div>'
            '<p style="font-size:0.76rem;color:var(--text-tertiary);line-height:1.65;margin:0 0 0.8rem;">Generate a professional LOI: select building, fill in lease details, download ready-to-send proposal.</p>'
            '<div style="display:flex;gap:0.3rem;flex-wrap:wrap;justify-content:center;">'
            '<span class="badge badge-green">3 Buildings</span>'
            '<span class="badge badge-amber">Download .docx</span>'
            '</div></div>'.format(cs=CARD_STYLE, ic=ICON_STYLE),
            unsafe_allow_html=True,
        )
        if st.button("LEASE PROPOSAL", use_container_width=True, key="btn_proposal", type="primary"):
            st.session_state["app_mode"] = "proposal"
            st.rerun()

    # ── Quick Access Tabs ──────────────────────────────────
    st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;margin-bottom:0.8rem;">'
        '<div style="font-size:0.6rem;color:var(--text-muted);letter-spacing:2px;text-transform:uppercase;font-weight:700;">Quick Access</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    QA_ITEMS = [
        ("projects", "&#x1F4CA;", "Upcoming Projects"),
        ("buildings", "&#x1F3E2;", "Our Buildings"),
        ("brokers", "&#x1F4CB;", "Broker Database"),
        ("tenants", "&#x1F4C1;", "Tenant Folders"),
        ("calendar", "&#x1F4C5;", "Tenant Calendar"),
        ("rent", "&#x1F4B0;", "Rent Tracker"),
    ]

    qa_cols = st.columns(len(QA_ITEMS), gap="small")
    for idx, (mode, icon, label) in enumerate(QA_ITEMS):
        with qa_cols[idx]:
            st.markdown(
                '<div style="text-align:center;padding:0.6rem 0.3rem 0.2rem;">'
                '<div style="font-size:1.3rem;margin-bottom:0.3rem;">{icon}</div>'
                '<div style="font-size:0.62rem;font-weight:600;color:var(--text-tertiary);letter-spacing:0.3px;">{label}</div>'
                '</div>'.format(icon=icon, label=label),
                unsafe_allow_html=True,
            )
            if st.button("Open", use_container_width=True, key="btn_qa_{}".format(mode)):
                st.session_state["app_mode"] = mode
                st.rerun()

    st.markdown(
        '<div style="text-align:center;margin-top:2.5rem;padding:1rem 0;">'
        '<div style="font-size:0.6rem;color:var(--text-muted);letter-spacing:0.5px;font-weight:500;">PATTON &mdash; Patton Commercial Real Estate &mdash; Miami-Dade County, FL</div>'
        '</div>'
        '<div style="text-align:right;padding:0.5rem 0;margin-top:0.5rem;">'
        '<span style="font-size:0.52rem;color:var(--text-muted);letter-spacing:0.5px;font-style:italic;">Developed by Sacha Ariel</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── PROPERTY SEARCH MODE ──────────────────────────────────
from utils.geocoding import geocode, fetch_property_records, fetch_pois, SAMPLE_ADDRESSES
from utils.maps import render_map_2d, render_map_2d_widget, render_map_3d, map_links, COMP_COLORS, _distance_mi
from utils.property_data import NB, match_neighborhood, lookup_parcel, lookup_buildings, format_currency, format_number, ALL_SUBMARKETS, random_address
from utils.scoring import compute_scores
from utils.financials import compute_financials, sensitivity_table
from utils.zoning import get_zone_info, estimate_buildable, zoning_summary_html, MIAMI21_ZONES
from utils.market import get_competition, get_land_comps, get_dev_recommendation, market_summary_html, demo_summary_html, comp_table_html, land_comp_table_html
from utils.ai_summary import generate_summary
from utils.export import export_json, export_csv, export_markdown, export_professional_html, build_report_data
from utils.comps import fetch_comps_for_neighborhood, fetch_comps_around, external_search_links, rental_search_links
from utils.valuation import sales_comparison_approach, income_approach, cost_approach, reconcile, value_drivers_html
from utils.recommendation import generate_recommendation
from utils.devplan import compute_dev_plan, scenario_comparison
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd
import pydeck as pdk
import math


def _chart_layout(title="", height=300, x_title="", y_title=""):
    return dict(
        title=dict(text=title, font=dict(size=13, color="#0f172a")) if title else None,
        height=height,
        margin=dict(l=40, r=20, t=40 if title else 20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title=x_title, gridcolor="#e2e8f0", linecolor="#e2e8f0", zeroline=False),
        yaxis=dict(title=y_title, gridcolor="#e2e8f0", linecolor="#e2e8f0", zeroline=False),
        font=dict(family="Inter, sans-serif", size=11, color="#475569"),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter"),
    )


# ── Session State ──────────────────────────────────────────
for k, v in [
    ("address", ""), ("geo", None), ("nb_name", None), ("nb", None),
    ("records", []), ("parcel", None), ("pois", None), ("scores", None),
    ("financials", None), ("searched", False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    logo_html = ""
    if LOGO_B64:
        logo_html = '<img src="data:image/png;base64,{}" style="height:48px;margin-bottom:0.5rem;">'.format(LOGO_B64)
    st.markdown(
        '<div style="text-align:center;padding:1rem 0 0.5rem;">'
        '{}'
        '<div style="color:#fff;font-size:1.1rem;font-weight:700;letter-spacing:1px;">PATTON</div>'
        '<div style="color:#64748b;font-size:0.58rem;letter-spacing:2px;text-transform:uppercase;margin-top:2px;">Real Estate Intelligence</div>'
        '</div>'.format(logo_html),
        unsafe_allow_html=True,
    )
    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:0.8rem 0;"></div>', unsafe_allow_html=True)

    if st.button("Back to Home", use_container_width=True, key="btn_home_from_prop"):
        st.session_state["app_mode"] = "home"
        st.session_state["searched"] = False
        st.rerun()

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:0.6rem 0;"></div>', unsafe_allow_html=True)

    auto_analyze = st.session_state.pop("_auto_analyze", False)
    prefill = st.session_state.pop("_rand_addr", "")
    if prefill:
        st.session_state["addr_input"] = prefill

    addr_input = st.text_input("Enter Address", placeholder="e.g. 858 W Flagler St, Miami, FL", key="addr_input")

    sample = st.selectbox("Or pick a sample", [""] + SAMPLE_ADDRESSES, key="sample_pick")
    if sample and sample != st.session_state.address:
        addr_input = sample

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:0.6rem 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#94a3b8;font-size:0.55rem;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.3rem;">Random by Submarket</div>', unsafe_allow_html=True)
    submarket_pick = st.selectbox("", [""] + ALL_SUBMARKETS, key="submarket_pick")
    if submarket_pick:
        if st.button("RANDOM ADDRESS", use_container_width=True, key="btn_random"):
            rand_addr = random_address(submarket_pick)
            if rand_addr:
                st.session_state["_rand_addr"] = rand_addr
                st.session_state["_auto_analyze"] = True
                st.rerun()
            else:
                st.warning("No addresses found for " + submarket_pick)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:0.6rem 0;"></div>', unsafe_allow_html=True)

    analyze_clicked = st.button("ANALYZE", use_container_width=True, key="btn_analyze")

    if (analyze_clicked or auto_analyze) and addr_input.strip():
        st.session_state.address = addr_input.strip()
        with st.spinner("Geocoding..."):
            st.session_state.geo = geocode(st.session_state.address)
        with st.spinner("Matching neighborhood..."):
            nb_name, nb = match_neighborhood(st.session_state.address, st.session_state.geo)
            st.session_state.nb_name = nb_name
            st.session_state.nb = nb
        with st.spinner("Looking up records..."):
            st.session_state.records = fetch_property_records(st.session_state.address)
            st.session_state.parcel = lookup_parcel(st.session_state.address)
        st.session_state.pois = None
        st.session_state.financials = None
        st.session_state.scores = compute_scores(
            st.session_state.geo or {}, st.session_state.nb,
            st.session_state.records, None
        )
        st.session_state.searched = True
        st.rerun()

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:0.8rem 0;"></div>', unsafe_allow_html=True)

    if st.session_state.searched and st.session_state.scores:
        sc = st.session_state.scores
        st.markdown(
            '<div style="text-align:center;margin:0.5rem 0;">'
            '<div style="color:#94a3b8;font-size:0.55rem;letter-spacing:2px;text-transform:uppercase;">Investment Score</div>'
            '<div style="color:#fff;font-size:2.2rem;font-weight:800;">{}</div>'
            '<div style="color:{};font-size:0.65rem;font-weight:600;letter-spacing:1px;">{}</div>'
            '</div>'.format(
                sc["overall"],
                score_color(sc["overall"]),
                "STRONG" if sc["overall"] >= 70 else ("MODERATE" if sc["overall"] >= 40 else "WEAK"),
            ),
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="position:absolute;bottom:1rem;left:0;right:0;text-align:center;">'
        '<div style="color:#475569;font-size:0.52rem;letter-spacing:0.5px;">Patton Commercial Real Estate</div>'
        '<div style="color:#334155;font-size:0.48rem;margin-top:2px;">Miami-Dade County</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Property Search: waiting for input ────────────────────
if not st.session_state.searched:
    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:80px;">'.format(LOGO_B64)
    st.markdown(
        '<div class="welcome">'
        '{}'
        '<h1>Property Search</h1>'
        '<div class="wl"></div>'
        '<div class="ws">Enter an address in the sidebar to begin</div>'
        '</div>'.format(logo_tag),
        unsafe_allow_html=True,
    )
    st.stop()

# ── Header ─────────────────────────────────────────────────
geo = st.session_state.geo or {}
nb_name = st.session_state.nb_name
nb = st.session_state.nb
records = st.session_state.records or []
parcel = st.session_state.parcel
scores = st.session_state.scores or {}

nb_badge = '<span class="badge badge-green">{}</span>'.format(nb_name) if nb_name else '<span class="badge badge-amber">Unknown Area</span>'

hdr_logo = ""
if LOGO_B64:
    hdr_logo = '<img src="data:image/png;base64,{}">'.format(LOGO_B64)

st.markdown(
    '<div class="app-header">'
    '<div class="hd-left">{}<div><div class="hd-title">PATTON</div><div class="hd-sub">Real Estate Intelligence</div></div></div>'
    '<div style="display:flex;gap:0.5rem;align-items:center;">{}</div>'
    '</div>'.format(hdr_logo, nb_badge),
    unsafe_allow_html=True,
)

addr_display = st.session_state.address
meta_parts = []
if geo.get("city"):
    meta_parts.append(geo["city"])
if geo.get("zip"):
    meta_parts.append("ZIP " + geo["zip"])
if nb_name:
    meta_parts.append(nb_name)
if nb and nb.get("oz"):
    meta_parts.append("Opportunity Zone")

st.markdown(
    '<div class="addr-result">'
    '<div class="ar-addr">{}</div>'
    '<div class="ar-meta">{}</div>'
    '</div>'.format(addr_display, " &bull; ".join(meta_parts)),
    unsafe_allow_html=True,
)

# ── Tabs ───────────────────────────────────────────────────
tab_names = ["Overview", "Map", "Property", "Zoning", "Dev Plan", "Market", "Financial", "Valuation", "Risk", "AI Summary", "Best Rec", "Export"]
tabs = st.tabs(tab_names)

# ── TAB 0: Overview ───────────────────────────────────────
with tabs[0]:
    kpi_items = []
    if nb:
        mkt = nb.get("mkt", {})
        last_sales = nb.get("last_sales", [])
        n_comps = len(last_sales)
        price_range = mkt.get("range", "N/A")
        inv_mo = mkt.get("inv_mo", "N/A")
        ls_ratio = mkt.get("ls_ratio", "N/A")
        absorption = mkt.get("absorption", "N/A")

        kpi_items.append(kpi("Median Price", format_currency(mkt.get("med_price")), "Neighborhood"))
        kpi_items.append(kpi("Price / sqft", "${}".format(mkt.get("psf", "N/A")), "Per square foot"))
        kpi_items.append(kpi("Avg Rent", format_currency(mkt.get("rent")) + "/mo", "Monthly"))
        kpi_items.append(kpi("Gross Yield", "{}%".format(mkt.get("yield", "N/A")), "Annual"))
        kpi_items.append(kpi("YoY Growth", "+{}%".format(mkt.get("yoy", "N/A")), "Appreciation"))
        kpi_items.append(kpi("Days on Market", str(mkt.get("dom", "N/A")), "Average"))
    else:
        kpi_items.append(kpi("Latitude", str(geo.get("lat", "N/A")), "Geocoded"))
        kpi_items.append(kpi("Longitude", str(geo.get("lon", "N/A")), "Geocoded"))
        kpi_items.append(kpi("Records Found", str(len(records)), "Open Data"))
        kpi_items.append(kpi("Confidence", "{}%".format(geo.get("confidence", 0)), "Geocoding"))
    st.markdown('<div class="kpi-grid">{}</div>'.format("".join(kpi_items)), unsafe_allow_html=True)

    # Data methodology (clickable)
    if nb:
        mkt = nb.get("mkt", {})
        last_sales = nb.get("last_sales", [])
        n_comps = len(last_sales)
        with st.expander("How are these metrics calculated?"):
            st.markdown(
                '<div style="font-size:0.82rem;color:var(--text-secondary);line-height:1.8;">'
                '<b>Median Price</b> — Median of {n} recent comparable sales in the {hood} neighborhood. Range: {rng}.<br>'
                '<b>Price / sqft</b> — Total sale price divided by gross living area (sqft). Averaged across comparables.<br>'
                '<b>Avg Rent</b> — Average monthly rental asking price for similar properties. Based on current active rental listings in the submarket.<br>'
                '<b>Gross Yield</b> — Formula: <code>(Annual Rent / Purchase Price) x 100</code>. '
                'Calculated as ({rent} x 12) / {med} = {yld}%.<br>'
                '<b>YoY Growth</b> — Year-over-year price appreciation based on rolling 12-month median comparison vs prior year.<br>'
                '<b>Days on Market</b> — Average number of days from listing to contract for sold properties in the past 6 months.<br>'
                '<hr style="border:none;border-top:1px solid var(--border);margin:0.6rem 0;">'
                '<b>Data Sources:</b> Miami-Dade County Property Appraiser, MLS/Redfin API, OpenStreetMap, neighborhood comp database ({n} comps).<br>'
                '<b>Confidence:</b> Inventory {inv} months | List-to-Sale ratio {ls}% | Absorption rate {ab}%'
                '</div>'.format(
                    n=n_comps, hood=st.session_state.nb_name or "N/A",
                    rng=mkt.get("range", "N/A"),
                    rent=format_currency(mkt.get("rent")),
                    med=format_currency(mkt.get("med_price")),
                    yld=mkt.get("yield", "N/A"),
                    inv=mkt.get("inv_mo", "N/A"),
                    ls=mkt.get("ls_ratio", "N/A"),
                    ab=mkt.get("absorption", "N/A"),
                ),
                unsafe_allow_html=True,
            )

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="card"><div class="card-title">Score Breakdown</div>', unsafe_allow_html=True)
        bars = ""
        for label, key in [("Location", "location"), ("Market", "market"), ("Financial", "financial"), ("Risk", "risk"), ("Data Confidence", "data_confidence")]:
            bars += score_bar(label, scores.get(key, 0))
        st.markdown('{}</div>'.format(bars), unsafe_allow_html=True)

        if nb:
            st.markdown('<div class="card"><div class="card-title">{}</div>'
                '<p style="font-size:0.82rem;color:var(--slate-500);line-height:1.6;margin:0;">{}</p>'
                '</div>'.format(nb.get("tagline", ""), nb.get("desc", "")), unsafe_allow_html=True)

    with c2:
        if geo.get("lat"):
            st.markdown('<div class="card"><div class="card-title">Quick Map</div>', unsafe_allow_html=True)
            render_map_2d_widget(geo["lat"], geo["lon"], label=addr_display, radius_miles=1)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warn">Geocoding failed. Map unavailable.</div>', unsafe_allow_html=True)

        if nb:
            hl_html = '<div class="card"><div class="card-title">Key Highlights</div><ul style="font-size:0.8rem;color:var(--slate-700);line-height:1.8;margin:0;padding-left:1rem;">'
            for h in nb.get("highlights", []):
                hl_html += "<li>{}</li>".format(h)
            hl_html += "</ul></div>"
            st.markdown(hl_html, unsafe_allow_html=True)


# ── TAB 1: Map ────────────────────────────────────────────
with tabs[1]:
    if not geo.get("lat"):
        st.markdown('<div class="alert-warn">Geocoding failed. Maps unavailable.</div>', unsafe_allow_html=True)
    else:
        mc1, mc2, mc3 = st.columns([2, 2, 1])
        with mc1:
            map_sub = st.radio("View", ["2D Map", "3D Massing", "External Links"], horizontal=True, key="map_type")
        with mc2:
            radius_mi = st.select_slider("Radius", options=[0.5, 1.0, 1.5, 2.0, 3.0], value=1.5, key="map_radius")
        with mc3:
            show_sold = st.checkbox("Sales", value=True, key="map_sold")
            show_active = st.checkbox("Active", value=True, key="map_active")

        map_comps = []
        if show_sold and geo.get("lat"):
            sold = fetch_comps_around(geo["lat"], geo["lon"], radius_mi, "sold")
            if not sold and nb_name:
                sold = fetch_comps_for_neighborhood(nb_name, "sold")
            for s in (sold or []):
                if s.get("lat") and s.get("lon"):
                    map_comps.append({
                        "lat": s["lat"], "lon": s["lon"],
                        "addr": s.get("address", ""),
                        "price": s.get("price", 0),
                        "type": s.get("type", ""),
                        "comp_type": "sale",
                        "source": "Redfin",
                    })

        if show_active and geo.get("lat"):
            active = fetch_comps_around(geo["lat"], geo["lon"], radius_mi, "active")
            if not active and nb_name:
                active = fetch_comps_for_neighborhood(nb_name, "active")
            for a in (active or []):
                if a.get("lat") and a.get("lon"):
                    map_comps.append({
                        "lat": a["lat"], "lon": a["lon"],
                        "addr": a.get("address", ""),
                        "price": a.get("price", 0),
                        "type": a.get("type", ""),
                        "comp_type": "rent" if "rent" in a.get("type", "").lower() else "sale",
                        "source": "Redfin",
                    })

        if nb and nb.get("last_sales"):
            for s in nb["last_sales"]:
                pg = geocode(s["addr"] + ", Miami, FL")
                if pg.get("lat"):
                    map_comps.append({
                        "lat": pg["lat"], "lon": pg["lon"],
                        "addr": s["addr"],
                        "price": s.get("price", 0),
                        "type": s.get("type", ""),
                        "comp_type": "sale",
                        "source": "Database",
                    })

        if map_sub == "2D Map":
            mp = render_map_2d(geo["lat"], geo["lon"], label=addr_display, comps=map_comps, radius_miles=radius_mi, show_legend=True)
            st_folium(mp, width=None, height=550, returned_objects=[])

        elif map_sub == "3D Massing":
            color_mode = st.radio("Color by", ["Type", "Value"], horizontal=True, key="3d_color")
            render_map_3d(geo["lat"], geo["lon"], label=addr_display, comps=map_comps,
                          color_mode="value" if color_mode == "Value" else "type")

        else:
            links = map_links(geo["lat"], geo["lon"], st.session_state.address)
            st.markdown('<div class="card"><div class="card-title">External Map Links</div>', unsafe_allow_html=True)
            for name, url in links.items():
                st.markdown('<a href="{}" target="_blank" style="display:block;padding:0.4rem 0;font-size:0.82rem;color:var(--blue);text-decoration:none;border-bottom:1px solid var(--slate-100);">{} &rarr;</a>'.format(url, name), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if map_comps and map_sub != "External Links":
            st.markdown('<div class="card"><div class="card-title">Visible Comparables ({} properties)</div>'.format(len(map_comps)), unsafe_allow_html=True)
            comp_rows = []
            for c in map_comps:
                dist = _distance_mi(geo["lat"], geo["lon"], c["lat"], c["lon"])
                comp_rows.append({
                    "Address": c.get("addr", "N/A"),
                    "Price": format_currency(c["price"]) if c.get("price") else "N/A",
                    "Type": c.get("type", "N/A"),
                    "Category": c.get("comp_type", "").title(),
                    "Distance": "{:.2f} mi".format(dist),
                    "Source": c.get("source", ""),
                })
            st.dataframe(pd.DataFrame(comp_rows).astype(str), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="card" style="padding:0.6rem 1rem;">'
            '<div style="display:flex;gap:1.2rem;flex-wrap:wrap;align-items:center;font-size:0.72rem;">'
            '<span style="font-weight:700;color:var(--navy);">Legend:</span>'
            '<span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#0f172a;margin-right:4px;"></span>Subject</span>'
            '<span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#2563eb;margin-right:4px;"></span>Sale Comps</span>'
            '<span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#16a34a;margin-right:4px;"></span>Rental</span>'
            '<span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#7c3aed;margin-right:4px;"></span>Development</span>'
            '<span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#dc2626;margin-right:4px;"></span>Risk</span>'
            '</div></div>',
            unsafe_allow_html=True,
        )


# ── TAB 2: Property ───────────────────────────────────────
with tabs[2]:
    if parcel:
        st.markdown('<div class="card"><div class="card-title">Parcel Record <span class="source-tag">LOCAL DB</span></div>', unsafe_allow_html=True)
        rows = ""
        rows += tr("Folio #", parcel.get("FOLIO #", "N/A"))
        rows += tr("Owner", parcel.get("true_owner1", "N/A"))
        rows += tr("Land Use", parcel.get("LAND USE", "N/A"))
        rows += tr("Lot Size", "{} sqft".format(format_number(parcel.get("LOT SIZE"))))
        rows += tr("Building Area", "{} sqft".format(format_number(parcel.get("BUILDING AREA"))))
        rows += tr("Year Built", str(parcel.get("YEAR BUILT", "N/A")))
        rows += tr("Zoning", parcel.get("ZONING CODE", "N/A"))
        sp = parcel.get("SALE PRICE")
        sale_str = "N/A"
        if sp and str(sp).replace(",", "").isdigit():
            sale_str = "${:,}".format(int(str(sp).replace(",", "")))
        rows += tr("Last Sale Price", sale_str)
        rows += tr("Sale Date", str(parcel.get("SALE DATE", "N/A")))
        st.markdown('<table class="dtable">{}</table></div>'.format(rows), unsafe_allow_html=True)
    else:
        pass  # Silently skip if no parcel data

    if records:
        st.markdown('<div class="card"><div class="card-title">Miami-Dade Open Data ({} records) <span class="source-tag">API</span></div>'.format(len(records)), unsafe_allow_html=True)
        cols = ["folio", "site_addr", "site_city", "site_zip", "owner1", "land_use_desc", "year_built", "actual_val"]
        disp = []
        for r in records:
            row = {}
            for c in cols:
                row[c] = r.get(c, "")
            disp.append(row)
        df = pd.DataFrame(disp).astype(str)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    # Silently skip if no records

    # Properties within 1 mile
    if geo.get("lat"):
        with st.spinner("Loading nearby properties..."):
            nearby_sold = fetch_comps_around(geo["lat"], geo["lon"], radius_mi=1, status="sold")
            nearby_active = fetch_comps_around(geo["lat"], geo["lon"], radius_mi=1, status="active")
        all_nearby = (nearby_active or []) + (nearby_sold or [])
        if all_nearby:
            st.markdown('<div class="card"><div class="card-title">Properties Within 1 Mile ({} found)</div>'.format(len(all_nearby)), unsafe_allow_html=True)
            prop_rows = []
            for p in all_nearby:
                dist = _distance_mi(geo["lat"], geo["lon"], p["lat"], p["lon"]) if p.get("lat") and p.get("lon") else None
                prop_rows.append({
                    "Address": p.get("address", "N/A"),
                    "Price": format_currency(p["price"]) if p.get("price") else "N/A",
                    "Type": p.get("type", "N/A"),
                    "Beds": str(p.get("beds", "")) if p.get("beds") is not None else "-",
                    "Baths": str(p.get("baths", "")) if p.get("baths") is not None else "-",
                    "Sqft": format_number(p.get("sqft")) if p.get("sqft") else "-",
                    "$/Sqft": "${:.0f}".format(p["psf"]) if p.get("psf") else "-",
                    "Year": str(p.get("year_built", "-")),
                    "Status": p.get("status", "N/A"),
                    "DOM": str(p.get("dom", "-")) if p.get("dom") is not None else "-",
                    "Distance": "{:.2f} mi".format(dist) if dist else "-",
                })
            df_nearby = pd.DataFrame(prop_rows).astype(str)
            st.dataframe(df_nearby, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-info">No properties found within 1 mile radius.</div>', unsafe_allow_html=True)


# ── TAB 3: Zoning ─────────────────────────────────────────
with tabs[3]:
    zone_code = None
    if parcel and parcel.get("ZONING CODE"):
        zone_code = parcel["ZONING CODE"]
    elif nb:
        zone_code = nb.get("zoning", {}).get("primary", "")

    zone_info = get_zone_info(zone_code) if zone_code else None
    nb_zoning = nb.get("zoning", {}) if nb else {}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="card-title">Zoning Details</div>', unsafe_allow_html=True)
        st.markdown(zoning_summary_html(zone_info, nb_zoning), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="card-title">Development Potential</div>', unsafe_allow_html=True)
        lot_sf = 0
        if parcel and parcel.get("LOT SIZE"):
            try:
                lot_sf = int(str(parcel["LOT SIZE"]).replace(",", ""))
            except (ValueError, TypeError):
                pass
        far_val = 0
        if zone_info and zone_info.get("max_far"):
            try:
                far_val = float(zone_info["max_far"])
            except (ValueError, TypeError):
                pass
        elif nb_zoning.get("max_far"):
            try:
                far_val = float(nb_zoning["max_far"])
            except (ValueError, TypeError):
                pass

        if lot_sf and far_val:
            bp = estimate_buildable(lot_sf, far_val)
            bp_rows = ""
            bp_rows += tr("Lot Size", "{:,} sqft".format(bp["lot_sf"]))
            bp_rows += tr("FAR", str(bp["far"]))
            bp_rows += tr("Gross Floor Area", "{:,} sqft".format(bp["gross_floor_area"]))
            bp_rows += tr("Net Rentable", "{:,} sqft".format(bp["net_rentable"]))
            bp_rows += tr("Est. Units (850sf avg)", str(bp["est_units"]))
            st.markdown('<table class="dtable">{}</table>'.format(bp_rows), unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-info">Enter lot size and FAR in the Dev Plan tab for detailed analysis.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">Miami 21 Zoning Reference</div>', unsafe_allow_html=True)
    zone_ref = []
    for code, info in MIAMI21_ZONES.items():
        zone_ref.append({"Code": code, "Name": info["name"], "Max Height": str(info["max_height"]), "Max FAR": str(info["max_far"]), "Parking": info["parking"]})
    st.dataframe(pd.DataFrame(zone_ref).astype(str), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── TAB 4: Dev Plan ───────────────────────────────────────
with tabs[4]:
    default_lot = 5000
    default_far = 3.5
    default_max_ht = 65
    default_max_fl = 5
    default_land = 0
    default_cons = 250
    default_rent_res = 2500

    if parcel:
        try:
            default_lot = int(str(parcel.get("LOT SIZE") or 5000).replace(",", ""))
        except (ValueError, TypeError):
            pass
        try:
            sp = int(str(parcel.get("SALE PRICE") or 0).replace(",", ""))
            if sp > 0:
                default_land = sp
        except (ValueError, TypeError):
            pass

    if nb:
        mkt_d = nb.get("mkt", {})
        if mkt_d.get("rent"):
            default_rent_res = mkt_d["rent"]
        z = nb.get("zoning", {})
        if z.get("max_far"):
            try:
                default_far = float(z["max_far"])
            except (ValueError, TypeError):
                pass
        if z.get("max_height"):
            ht_str = str(z["max_height"]).replace("ft", "").replace("'", "").strip()
            try:
                default_max_ht = int(ht_str)
            except (ValueError, TypeError):
                pass

    st.markdown('<div class="card"><div class="card-title">Development Plan Generator <span class="source-tag">CALCULATOR</span></div>', unsafe_allow_html=True)

    dc1, dc2, dc3, dc4 = st.columns(4)
    with dc1:
        st.markdown('<div style="font-size:0.65rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:0.3rem;">Site & Zoning</div>', unsafe_allow_html=True)
        dp_lot = st.number_input("Lot Size (sqft)", value=default_lot, step=500, min_value=500, key="dp_lot")
        dp_far = st.number_input("FAR", value=min(default_far, 50.0), step=0.5, min_value=0.5, max_value=50.0, key="dp_far")
        dp_max_ht = st.number_input("Max Height (ft)", value=max(default_max_ht, 20), step=5, min_value=20, key="dp_ht")
        dp_max_fl = st.number_input("Max Floors", value=max(default_max_fl, 1), step=1, min_value=1, key="dp_fl")
        dp_floor_eff = st.slider("Floor Efficiency %", 60, 95, 80, key="dp_fe")
    with dc2:
        st.markdown('<div style="font-size:0.65rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:0.3rem;">Unit Mix</div>', unsafe_allow_html=True)
        dp_rent_eff = st.slider("Rentable Efficiency %", 70, 95, 85, key="dp_re")
        dp_avg_unit = st.number_input("Avg Unit Size (sqft)", value=850, step=50, min_value=300, key="dp_unit")
        dp_res = st.slider("Residential %", 0, 100, 85, key="dp_res")
        dp_office = st.slider("Office %", 0, 100, 10, key="dp_off")
        dp_retail = st.slider("Retail %", 0, 100, 5, key="dp_ret")
    with dc3:
        st.markdown('<div style="font-size:0.65rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:0.3rem;">Costs & Revenue</div>', unsafe_allow_html=True)
        dp_parking = st.number_input("Parking Ratio", value=1.0, step=0.25, min_value=0.0, key="dp_park")
        dp_cons = st.number_input("Construction $/sqft", value=default_cons, step=10, min_value=100, key="dp_cons")
        dp_soft = st.slider("Soft Cost %", 10, 40, 25, key="dp_soft")
        dp_land = st.number_input("Land Price ($)", value=default_land, step=10000, min_value=0, key="dp_land")
        dp_rent = st.number_input("Target Rent (res $/mo)", value=default_rent_res, step=100, min_value=500, key="dp_rent")
    with dc4:
        st.markdown('<div style="font-size:0.65rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:0.3rem;">Financing</div>', unsafe_allow_html=True)
        dp_rent_off = st.number_input("Office Rent $/sf/yr", value=35, step=5, min_value=10, key="dp_roff")
        dp_rent_ret = st.number_input("Retail Rent $/sf/yr", value=40, step=5, min_value=10, key="dp_rret")
        dp_exit_cap = st.number_input("Exit Cap Rate %", value=5.0, step=0.25, min_value=2.0, key="dp_cap")
        dp_int = st.number_input("Interest Rate %", value=7.0, step=0.25, min_value=2.0, key="dp_int")
        dp_ltv = st.slider("LTV %", 30, 90, 65, key="dp_ltv")
    st.markdown('</div>', unsafe_allow_html=True)

    dp_inputs = {
        "lot_sf": dp_lot, "far": dp_far, "max_height_ft": dp_max_ht, "max_floors": dp_max_fl,
        "floor_efficiency": dp_floor_eff / 100.0, "rentable_efficiency": dp_rent_eff / 100.0,
        "avg_unit_sf": dp_avg_unit, "res_pct": dp_res, "office_pct": dp_office, "retail_pct": dp_retail,
        "parking_ratio": dp_parking, "construction_psf": dp_cons, "soft_cost_pct": dp_soft,
        "land_price": dp_land, "target_rent_res": dp_rent, "target_rent_office": dp_rent_off,
        "target_rent_retail": dp_rent_ret, "exit_cap": dp_exit_cap, "interest_rate": dp_int,
        "ltv": dp_ltv, "opex_ratio": 35,
    }
    dp = compute_dev_plan(dp_inputs)

    dp_kpi = []
    dp_kpi.append(kpi("Buildable GSF", "{:,}".format(dp["actual_gsf"]), "{} floors".format(dp["est_floors"])))
    dp_kpi.append(kpi("Rentable SF", "{:,}".format(dp["rentable_sf"]), "Net"))
    dp_kpi.append(kpi("Est. Units", str(dp["est_units"]), "{} sqft avg".format(dp["avg_unit_sf"])))
    dp_kpi.append(kpi("Total Dev Cost", format_currency(dp["total_dev_cost"]), "All-in"))
    profit_color = "var(--green)" if dp["profit"] > 0 else "var(--red)"
    dp_kpi.append(kpi("Profit", format_currency(dp["profit"]), "{:.1f}% margin".format(dp["profit_margin"])))
    dp_kpi.append(kpi("Return on Cost", "{:.1f}%".format(dp["return_on_cost"]), "Yield on cost"))
    st.markdown('<div class="kpi-grid">{}</div>'.format("".join(dp_kpi)), unsafe_allow_html=True)

    dp1, dp2, dp3 = st.columns(3)
    with dp1:
        st.markdown('<div class="card"><div class="card-title">Building Program</div>', unsafe_allow_html=True)
        rows = ""
        rows += tr("Lot Size", "{:,} sqft".format(dp["lot_sf"]))
        rows += tr("Max Allowed GSF", "{:,} sqft".format(int(dp["max_gsf"])))
        rows += tr("Actual GSF", "{:,} sqft".format(dp["actual_gsf"]))
        rows += tr("Floor Plate", "{:,} sqft".format(dp["floor_plate"]))
        rows += tr("Floors", str(dp["est_floors"]))
        rows += tr("Height", "{} ft".format(dp["building_height_ft"]))
        rows += tr("Residential", "{:,} sqft".format(dp["res_sf"]))
        rows += tr("Office", "{:,} sqft".format(dp["office_sf"]))
        rows += tr("Retail", "{:,} sqft".format(dp["retail_sf"]))
        rows += tr("Parking Spaces", str(dp["parking_spaces"]))
        st.markdown('<table class="dtable">{}</table></div>'.format(rows), unsafe_allow_html=True)

    with dp2:
        st.markdown('<div class="card"><div class="card-title">Cost Breakdown</div>', unsafe_allow_html=True)
        rows = ""
        rows += tr("Hard Costs", format_currency(dp["hard_cost"]))
        rows += tr("Soft Costs", format_currency(dp["soft_cost"]))
        rows += tr("Parking", format_currency(dp["parking_cost"]))
        rows += tr("Land", format_currency(dp["land_price"]))
        rows += '<tr><td class="dk" style="font-weight:700;">Total Dev Cost</td><td class="dv" style="font-weight:700;">{}</td></tr>'.format(format_currency(dp["total_dev_cost"]))
        rows += '<tr><td colspan="2" style="height:6px;"></td></tr>'
        rows += tr("Loan Amount", format_currency(dp["loan_amount"]))
        rows += tr("Equity Required", format_currency(dp["equity"]))
        rows += tr("Annual Debt Service", format_currency(dp["annual_ds"]))
        st.markdown('<table class="dtable">{}</table></div>'.format(rows), unsafe_allow_html=True)

    with dp3:
        st.markdown('<div class="card"><div class="card-title">Returns & Income</div>', unsafe_allow_html=True)
        rows = ""
        rows += tr("Gross Income", format_currency(dp["gross_income"]))
        rows += tr("Vacancy", "-{}".format(format_currency(dp["vacancy_loss"])))
        rows += tr("EGI", format_currency(dp["egi"]))
        rows += tr("OpEx", "-{}".format(format_currency(dp["opex"])))
        rows += '<tr><td class="dk" style="font-weight:700;">NOI</td><td class="dv" style="font-weight:700;">{}</td></tr>'.format(format_currency(dp["noi"]))
        rows += '<tr><td colspan="2" style="height:6px;"></td></tr>'
        rows += tr("Value at Exit Cap", format_currency(dp["value_at_cap"]))
        rows += tr("DSCR", "{:.2f}x".format(dp["dscr"]))
        pf_color = "var(--green)" if dp["profit"] > 0 else "var(--red)"
        rows += '<tr><td class="dk" style="font-weight:700;">Profit</td><td class="dv" style="font-weight:700;color:{};">{}</td></tr>'.format(pf_color, format_currency(dp["profit"]))
        st.markdown('<table class="dtable">{}</table></div>'.format(rows), unsafe_allow_html=True)

    # Zoning Compliance
    st.markdown('<div class="card"><div class="card-title">Zoning Compliance Check</div>', unsafe_allow_html=True)
    for check in dp.get("zoning_checks", []):
        badge_cls = "zcheck-pass" if check["status"] == "pass" else "zcheck-fail"
        badge_txt = "PASS" if check["status"] == "pass" else "FAIL"
        st.markdown(
            '<div class="zcheck">'
            '<span class="zcheck-label">{}</span>'
            '<div style="display:flex;align-items:center;gap:0.5rem;">'
            '<span style="font-size:0.75rem;color:var(--slate-500);">{}</span>'
            '<span class="zcheck-badge {}">{}</span>'
            '</div></div>'.format(check["item"], check["detail"], badge_cls, badge_txt),
            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Scenario Comparison
    st.markdown('<div class="card"><div class="card-title">Scenario Comparison</div>', unsafe_allow_html=True)
    scenarios = scenario_comparison(dp_inputs)
    sc_html = '<div class="scenario-grid">'
    for label, sc_key in [("Conservative", "conservative"), ("Base Case", "base"), ("Upside", "upside")]:
        s = scenarios[sc_key]
        active = " active" if sc_key == "base" else ""
        pf_clr = "#16a34a" if s["profit"] > 0 else "#dc2626"
        sc_html += (
            '<div class="scenario-card{}">'
            '<div class="scenario-label">{}</div>'
            '<div class="scenario-value" style="color:{};">{}</div>'
            '<div class="scenario-sub">Profit</div>'
            '<div style="margin-top:0.5rem;font-size:0.7rem;color:var(--slate-500);">'
            'ROC: {:.1f}% | DSCR: {:.2f}x<br>'
            'NOI: {} | Margin: {:.0f}%'
            '</div></div>'.format(
                active, label, pf_clr, format_currency(s["profit"]),
                s["return_on_cost"], s["dscr"],
                format_currency(s["noi"]), s["profit_margin"],
            ))
    sc_html += '</div>'
    st.markdown(sc_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 3D Massing Visualization
    if geo.get("lat"):
        st.markdown('<div class="card"><div class="card-title">3D Massing Envelope</div>', unsafe_allow_html=True)
        mass_data = [{
            "lat": geo["lat"], "lon": geo["lon"],
            "height": dp["building_height_ft"],
            "color": [37, 99, 235, 180], "name": "Proposed Building",
        }]
        mass_layer = pdk.Layer(
            "ColumnLayer", data=mass_data,
            get_position=["lon", "lat"], get_elevation="height",
            elevation_scale=50, get_fill_color="color", radius=max(12, int(math.sqrt(dp["floor_plate"]) / 3)),
            pickable=True,
        )
        zoning_env = [{
            "lat": geo["lat"], "lon": geo["lon"] + 0.0003,
            "height": dp["max_height_ft"],
            "color": [220, 38, 38, 60], "name": "Zoning Envelope (max)",
        }]
        env_layer = pdk.Layer(
            "ColumnLayer", data=zoning_env,
            get_position=["lon", "lat"], get_elevation="height",
            elevation_scale=50, get_fill_color="color", radius=max(12, int(math.sqrt(dp["floor_plate"]) / 3)),
            pickable=True,
        )
        view = pdk.ViewState(latitude=geo["lat"], longitude=geo["lon"], zoom=17, pitch=55, bearing=-15)
        deck = pdk.Deck(layers=[mass_layer, env_layer], initial_view_state=view, map_style="light",
                        tooltip={"text": "{name}\nHeight: {height} ft"})
        st.pydeck_chart(deck)
        st.markdown(
            '<div style="display:flex;gap:1rem;font-size:0.72rem;margin-top:0.5rem;">'
            '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:rgba(37,99,235,0.7);margin-right:4px;"></span>Proposed Building</span>'
            '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:rgba(220,38,38,0.25);margin-right:4px;"></span>Zoning Envelope</span>'
            '</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── TAB 5: Market ──────────────────────────────────────────
with tabs[5]:
    if nb:
        mkt = nb.get("mkt", {})
        demo = nb.get("demo", {})

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card"><div class="card-title">Market Metrics <span class="source-tag">DATABASE</span></div>', unsafe_allow_html=True)
            st.markdown(market_summary_html(mkt, demo), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="card"><div class="card-title">Demographics <span class="source-tag">DATABASE</span></div>', unsafe_allow_html=True)
            st.markdown(demo_summary_html(demo), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">Live Market Data <span class="source-tag">REDFIN MLS</span></div>'
        '<div style="font-size:0.72rem;color:var(--slate-500);margin-bottom:0.5rem;">Updated every 30 minutes from Redfin MLS.</div>', unsafe_allow_html=True)

    mkt_mode = st.radio("View", ["Active Listings", "Recently Sold", "Both"], horizontal=True, key="mkt_mode")

    active_comps = []
    sold_comps = []
    if geo.get("lat"):
        if mkt_mode in ["Active Listings", "Both"]:
            with st.spinner("Fetching active listings..."):
                if nb_name:
                    active_comps = fetch_comps_for_neighborhood(nb_name, "active")
                if not active_comps:
                    active_comps = fetch_comps_around(geo["lat"], geo["lon"], 1.5, "active")
        if mkt_mode in ["Recently Sold", "Both"]:
            with st.spinner("Fetching recent sales..."):
                if nb_name:
                    sold_comps = fetch_comps_for_neighborhood(nb_name, "sold")
                if not sold_comps:
                    sold_comps = fetch_comps_around(geo["lat"], geo["lon"], 1.5, "sold")
    st.markdown('</div>', unsafe_allow_html=True)

    if active_comps:
        st.markdown('<div class="card"><div class="card-title">Active Listings ({} properties)</div>'.format(len(active_comps)), unsafe_allow_html=True)
        act_df = pd.DataFrame(active_comps)
        show_cols = ["address", "price", "beds", "baths", "sqft", "psf", "type", "dom", "lot_sf", "year_built"]
        show_cols = [c for c in show_cols if c in act_df.columns]
        act_display = act_df[show_cols].copy()
        def _fmt_cur(x):
            try: return "${:,}".format(int(x)) if x else "N/A"
            except (ValueError, TypeError): return str(x) if x else "N/A"
        def _fmt_num(x):
            try: return "{:,}".format(int(x)) if x else ""
            except (ValueError, TypeError): return str(x) if x else ""
        def _fmt_psf(x):
            try: return "${:.0f}".format(float(x)) if x else ""
            except (ValueError, TypeError): return str(x) if x else ""
        if "price" in act_display.columns:
            act_display["price"] = act_display["price"].apply(_fmt_cur)
        if "sqft" in act_display.columns:
            act_display["sqft"] = act_display["sqft"].apply(_fmt_num)
        if "lot_sf" in act_display.columns:
            act_display["lot_sf"] = act_display["lot_sf"].apply(_fmt_num)
        if "psf" in act_display.columns:
            act_display["psf"] = act_display["psf"].apply(_fmt_psf)
        act_display.columns = [c.replace("_", " ").title() for c in act_display.columns]
        st.dataframe(act_display.astype(str), use_container_width=True, hide_index=True)

        if "price" in act_df.columns:
            prices = [p for p in act_df["price"] if p and p > 0]
            if prices:
                kpi_row = []
                kpi_row.append(kpi("Median List", format_currency(sorted(prices)[len(prices) // 2]), "{} listings".format(len(prices))))
                kpi_row.append(kpi("Low", format_currency(min(prices)), "Cheapest"))
                kpi_row.append(kpi("High", format_currency(max(prices)), "Most expensive"))
                avg_psf_vals = [p for p in act_df["psf"] if p and p > 0]
                if avg_psf_vals:
                    kpi_row.append(kpi("Avg $/SF", "${:.0f}".format(sum(avg_psf_vals) / len(avg_psf_vals)), "Active listings"))
                avg_dom_vals = [d for d in act_df["dom"] if d is not None and d >= 0]
                if avg_dom_vals:
                    kpi_row.append(kpi("Avg DOM", str(int(sum(avg_dom_vals) / len(avg_dom_vals))), "Days on market"))
                st.markdown('<div class="kpi-grid">{}</div>'.format("".join(kpi_row)), unsafe_allow_html=True)

        with st.expander("View Redfin Links"):
            for comp in active_comps[:20]:
                if comp.get("url"):
                    label = "{} - {}".format(comp["address"], format_currency(comp["price"]) if comp["price"] else "N/A")
                    st.markdown("[{}]({})".format(label, comp["url"]))
        st.markdown('</div>', unsafe_allow_html=True)

    if sold_comps:
        st.markdown('<div class="card"><div class="card-title">Recently Sold ({} properties, last 12 months)</div>'.format(len(sold_comps)), unsafe_allow_html=True)
        sold_df = pd.DataFrame(sold_comps)
        show_cols = ["address", "price", "beds", "baths", "sqft", "psf", "type", "sold_date", "lot_sf"]
        show_cols = [c for c in show_cols if c in sold_df.columns]
        sold_display = sold_df[show_cols].copy()
        if "price" in sold_display.columns:
            sold_display["price"] = sold_display["price"].apply(_fmt_cur)
        if "sqft" in sold_display.columns:
            sold_display["sqft"] = sold_display["sqft"].apply(_fmt_num)
        if "lot_sf" in sold_display.columns:
            sold_display["lot_sf"] = sold_display["lot_sf"].apply(_fmt_num)
        if "psf" in sold_display.columns:
            sold_display["psf"] = sold_display["psf"].apply(_fmt_psf)
        sold_display.columns = [c.replace("_", " ").title() for c in sold_display.columns]
        st.dataframe(sold_display.astype(str), use_container_width=True, hide_index=True)

        if "price" in sold_df.columns:
            prices = [p for p in sold_df["price"] if p and p > 0]
            if prices:
                kpi_row = []
                kpi_row.append(kpi("Median Sold", format_currency(sorted(prices)[len(prices) // 2]), "{} sold".format(len(prices))))
                kpi_row.append(kpi("Low", format_currency(min(prices)), "Cheapest sale"))
                kpi_row.append(kpi("High", format_currency(max(prices)), "Highest sale"))
                st.markdown('<div class="kpi-grid">{}</div>'.format("".join(kpi_row)), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if not active_comps and not sold_comps:
        st.markdown('<div class="alert-warn">Could not fetch live market data. Use the external links below to view listings.</div>', unsafe_allow_html=True)

    # External Search Links
    zip_code = geo.get("zip", nb.get("zip", "33130") if nb else "33130")
    sale_links = external_search_links(st.session_state.address, geo.get("lat", 0), geo.get("lon", 0), nb_name, zip_code)
    rent_links = rental_search_links(nb_name, zip_code)

    lc1, lc2 = st.columns(2)
    with lc1:
        st.markdown('<div class="card"><div class="card-title">For Sale Platforms</div>', unsafe_allow_html=True)
        for name, url in sale_links.items():
            st.markdown('<a href="{}" target="_blank" style="display:block;padding:0.4rem 0;font-size:0.82rem;color:var(--blue);text-decoration:none;border-bottom:1px solid var(--slate-100);">{} &rarr;</a>'.format(url, name), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with lc2:
        st.markdown('<div class="card"><div class="card-title">Rental Platforms</div>', unsafe_allow_html=True)
        for name, url in rent_links.items():
            st.markdown('<a href="{}" target="_blank" style="display:block;padding:0.4rem 0;font-size:0.82rem;color:var(--blue);text-decoration:none;border-bottom:1px solid var(--slate-100);">{} &rarr;</a>'.format(url, name), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Internal Data
    if nb:
        if nb.get("last_sales"):
            st.markdown('<div class="card"><div class="card-title">Neighborhood Sales <span class="source-tag">DATABASE</span></div>', unsafe_allow_html=True)
            sales_df = pd.DataFrame(nb["last_sales"])
            sales_df["price"] = sales_df["price"].apply(lambda x: "${:,}".format(x))
            sales_df["sqft"] = sales_df["sqft"].apply(lambda x: "{:,}".format(x))
            st.dataframe(sales_df.astype(str), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        comps = get_competition(nb_name)
        if comps:
            st.markdown('<div class="card"><div class="card-title">Competition Pipeline <span class="source-tag">DATABASE</span></div>', unsafe_allow_html=True)
            st.markdown(comp_table_html(comps), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        lc = get_land_comps(nb_name)
        if lc:
            st.markdown('<div class="card"><div class="card-title">Land Comps <span class="source-tag">DATABASE</span></div>', unsafe_allow_html=True)
            st.markdown(land_comp_table_html(lc), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        dev = get_dev_recommendation(nb_name)
        if dev:
            st.markdown('<div class="card"><div class="card-title">Development Recommendation</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.9rem;font-weight:700;color:var(--navy);margin-bottom:0.3rem;">{}</div>'.format(dev.get("best_product", "")), unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.82rem;color:var(--slate-700);line-height:1.6;margin:0 0 0.5rem;">{}</p>'.format(dev.get("rationale", "")), unsafe_allow_html=True)
            dev_rows = ""
            if dev.get("rooftop_rec"):
                dev_rows += tr("Rooftop", dev["rooftop_rec"])
            if dev.get("parking_rec"):
                dev_rows += tr("Parking", dev["parking_rec"])
            if dev.get("target_buyer"):
                dev_rows += tr("Target Buyer", dev["target_buyer"])
            if dev.get("construction"):
                c = dev["construction"]
                dev_rows += tr("Construction", c.get("type", ""))
                dev_rows += tr("Cost/sqft", c.get("cost_psf", ""))
                dev_rows += tr("Timeline", c.get("timeline", ""))
            if dev.get("comp_advantage"):
                dev_rows += tr("Competitive Edge", dev["comp_advantage"])
            if dev_rows:
                st.markdown('<table class="dtable">{}</table>'.format(dev_rows), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if nb.get("mkt"):
            sc = nb.get("scores", {})
            cats = ["Walk Score", "Transit Score", "Bike Score"]
            vals = [sc.get("walk", 0), sc.get("transit", 0), sc.get("bike", 0)]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=cats, y=vals, marker_color=["#2563eb", "#3b82f6", "#60a5fa"],
                                 text=vals, textposition="outside"))
            fig.update_layout(**_chart_layout("Walkability & Transit Scores", 300, y_title="Score"))
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)

    if not nb and not active_comps and not sold_comps:
        st.markdown('<div class="alert-warn">No neighborhood data available. Use the external platform links above to research this area.</div>', unsafe_allow_html=True)


# ── TAB 6: Financial ──────────────────────────────────────
with tabs[6]:
    default_price = 500000
    default_rent = 2200
    default_units = 1
    if nb:
        mkt = nb.get("mkt", {})
        default_price = mkt.get("med_price", 500000)
        default_rent = mkt.get("rent", 2200)
    if parcel:
        sp = parcel.get("SALE PRICE")
        if sp:
            try:
                parsed = int(str(sp).replace(",", ""))
                if parsed > 0:
                    default_price = parsed
            except (ValueError, TypeError):
                pass

    st.markdown('<div class="card"><div class="card-title">Assumptions <span class="source-tag">USER INPUT</span></div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        purchase = st.number_input("Purchase Price ($)", value=default_price, step=10000, min_value=10000, key="fin_price")
        down_pct = st.slider("Down Payment %", 0, 100, 25, key="fin_down")
        rate = st.slider("Interest Rate %", 0.0, 12.0, 7.0, 0.25, key="fin_rate")
    with fc2:
        term = st.selectbox("Loan Term (years)", [15, 20, 25, 30], index=3, key="fin_term")
        rent = st.number_input("Monthly Rent / Unit ($)", value=default_rent, step=50, min_value=0, key="fin_rent")
        units = st.number_input("Number of Units", value=default_units, step=1, min_value=1, key="fin_units")
    with fc3:
        vacancy = st.slider("Vacancy %", 0, 30, 5, key="fin_vac")
        opex_pct = st.slider("OpEx % of EGI", 0, 60, 35, key="fin_opex")
        tax_rate = st.slider("Tax Rate % of Value", 0.0, 5.0, 2.0, 0.1, key="fin_tax")
        mgmt_pct = st.slider("Management % of EGI", 0, 15, 8, key="fin_mgmt")
    st.markdown('</div>', unsafe_allow_html=True)

    fin_inputs = {
        "purchase": purchase, "down_pct": down_pct, "rate": rate, "term": term,
        "rent": rent, "units": units, "vacancy": vacancy, "opex_pct": opex_pct,
        "tax_rate": tax_rate, "mgmt_pct": mgmt_pct, "ins_rate": 0.5,
    }
    fin = compute_financials(fin_inputs)
    st.session_state.financials = fin
    st.session_state.scores = compute_scores(geo, nb, records, fin)
    scores = st.session_state.scores or {}

    kpi_items = []
    kpi_items.append(kpi("NOI", "${:,.0f}".format(fin["noi"]), "Annual"))
    kpi_items.append(kpi("Cap Rate", "{:.1f}%".format(fin["cap_rate"]), "NOI / Price"))
    kpi_items.append(kpi("Cash-on-Cash", "{:.1f}%".format(fin["coc"]), "CF / Equity"))
    kpi_items.append(kpi("DSCR", "{:.2f}x".format(fin["dscr"]), "NOI / Debt Service"))
    kpi_items.append(kpi("Monthly CF", "${:,.0f}".format(fin["cash_flow"] / 12), "After Debt"))
    kpi_items.append(kpi("Breakeven", "{:.0f}%".format(fin["breakeven"]), "Occupancy"))
    st.markdown('<div class="kpi-grid">{}</div>'.format("".join(kpi_items)), unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="card-title">Income Statement</div>', unsafe_allow_html=True)
        rows = ""
        rows += tr("Gross Potential Rent", "${:,.0f}".format(fin["gross_rent"]))
        rows += tr("Less: Vacancy", "-${:,.0f}".format(fin["vacancy_loss"]))
        rows += tr("Effective Gross Income", "${:,.0f}".format(fin["egi"]))
        rows += '<tr><td colspan="2" style="height:4px;background:var(--slate-100);"></td></tr>'
        rows += tr("Property Tax", "-${:,.0f}".format(fin["tax"]))
        rows += tr("Insurance", "-${:,.0f}".format(fin["insurance"]))
        rows += tr("Maintenance (1%)", "-${:,.0f}".format(fin["maintenance"]))
        rows += tr("Management", "-${:,.0f}".format(fin["management"]))
        rows += tr("Total OpEx", "-${:,.0f}".format(fin["opex"]))
        rows += '<tr><td colspan="2" style="height:4px;background:var(--slate-100);"></td></tr>'
        rows += '<tr><td class="dk" style="font-weight:700;">Net Operating Income</td><td class="dv" style="font-weight:700;font-size:1rem;">${:,.0f}</td></tr>'.format(fin["noi"])
        st.markdown('<table class="dtable">{}</table></div>'.format(rows), unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="card-title">Debt & Returns</div>', unsafe_allow_html=True)
        rows = ""
        rows += tr("Down Payment", "${:,.0f}".format(fin["down_payment"]))
        rows += tr("Loan Amount", "${:,.0f}".format(fin["loan"]))
        rows += tr("Monthly Payment", "${:,.0f}".format(fin["monthly_pmt"]))
        rows += tr("Annual Debt Service", "${:,.0f}".format(fin["debt_service"]))
        rows += '<tr><td colspan="2" style="height:4px;background:var(--slate-100);"></td></tr>'
        cf_color = "var(--green)" if fin["cash_flow"] > 0 else "var(--red)"
        rows += '<tr><td class="dk" style="font-weight:700;">Annual Cash Flow</td><td class="dv" style="font-weight:700;font-size:1rem;color:{};">${:,.0f}</td></tr>'.format(cf_color, fin["cash_flow"])
        rows += tr("GRM", "{:.1f}x".format(fin["grm"]))
        rows += tr("Value from Cap", format_currency(fin["val_from_cap"]))
        st.markdown('<table class="dtable">{}</table></div>'.format(rows), unsafe_allow_html=True)

    # Sensitivity
    s1, s2 = st.columns(2)
    with s1:
        rates_range = [r / 4 for r in range(int(max(rate - 2, 1) * 4), int((rate + 2.25) * 4), 1)]
        sens_rate = sensitivity_table(fin_inputs, "rate", rates_range, "cash_flow")
        fig = go.Figure()
        x_vals = [s["input"] for s in sens_rate]
        y_vals = [s["output"] / 12 for s in sens_rate]
        colors = ["#16a34a" if y > 0 else "#dc2626" for y in y_vals]
        fig.add_trace(go.Bar(x=x_vals, y=y_vals, marker_color=colors, hovertemplate="Rate: %{x}%<br>Monthly CF: $%{y:,.0f}<extra></extra>"))
        fig.update_layout(**_chart_layout("Monthly CF vs Interest Rate", 300, "Rate %", "Monthly CF ($)"))
        st.plotly_chart(fig, use_container_width=True)

    with s2:
        vac_range = list(range(0, 26, 2))
        sens_vac = sensitivity_table(fin_inputs, "vacancy", vac_range, "cash_flow")
        fig = go.Figure()
        x_vals = [s["input"] for s in sens_vac]
        y_vals = [s["output"] / 12 for s in sens_vac]
        colors = ["#16a34a" if y > 0 else "#dc2626" for y in y_vals]
        fig.add_trace(go.Bar(x=x_vals, y=y_vals, marker_color=colors, hovertemplate="Vacancy: %{x}%<br>Monthly CF: $%{y:,.0f}<extra></extra>"))
        fig.update_layout(**_chart_layout("Monthly CF vs Vacancy Rate", 300, "Vacancy %", "Monthly CF ($)"))
        st.plotly_chart(fig, use_container_width=True)


# ── TAB 7: Valuation ───────────────────────────────────────
with tabs[7]:
    subj_sqft = 0
    subj_beds = 0
    subj_year = 0
    subj_lot = 0
    if parcel:
        try:
            subj_sqft = int(str(parcel.get("BUILDING AREA") or 0).replace(",", ""))
        except (ValueError, TypeError):
            pass
        try:
            subj_lot = int(str(parcel.get("LOT SIZE") or 0).replace(",", ""))
        except (ValueError, TypeError):
            pass
        try:
            subj_year = int(str(parcel.get("YEAR BUILT") or 0))
            if subj_year < 1900:
                subj_year = 0
        except (ValueError, TypeError):
            pass

    st.markdown(value_drivers_html(nb, parcel, geo), unsafe_allow_html=True)

    val_comps = []
    if geo.get("lat"):
        val_comps = fetch_comps_around(geo["lat"], geo["lon"], 0.75, "sold")
        if not val_comps and nb_name:
            val_comps = fetch_comps_for_neighborhood(nb_name, "sold")

    sca = sales_comparison_approach(val_comps, subj_sqft or 1200, subj_beds, subj_year, subj_lot)

    vc1, vc2, vc3 = st.columns(3)

    with vc1:
        st.markdown('<div class="card"><div class="card-title">Sales Comparison</div>', unsafe_allow_html=True)
        if sca:
            st.markdown('<div style="text-align:center;padding:0.5rem 0;">'
                '<div style="font-size:0.6rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;">Indicated Value</div>'
                '<div style="font-size:1.6rem;font-weight:800;color:var(--navy);">{}</div>'
                '<div style="font-size:0.7rem;color:var(--slate-400);">Based on {} comparable sales</div>'
                '</div>'.format(format_currency(sca["indicated_value"]), sca["count"]),
                unsafe_allow_html=True)
            rows = ""
            rows += tr("Median Comp Price", format_currency(sca["median_price"]))
            rows += tr("Avg Comp Price", format_currency(sca["avg_price"]))
            rows += tr("Range", "{} - {}".format(format_currency(sca["min_price"]), format_currency(sca["max_price"])))
            if sca.get("median_psf"):
                rows += tr("Median $/SF", "${:.0f}".format(sca["median_psf"]))
            if sca.get("adjusted_psf"):
                rows += tr("Adjusted $/SF", "${:.0f}".format(sca["adjusted_psf"]))
            st.markdown('<table class="dtable">{}</table>'.format(rows), unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warn">Not enough comparable sales data.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    fin = st.session_state.get("financials")
    market_cap = 0
    if nb:
        mkt_data = nb.get("mkt", {})
        gross_yield = mkt_data.get("yield", 0)
        market_cap = gross_yield * 0.65 if gross_yield else 5.0
    noi_val = fin.get("noi", 0) if fin else 0
    if not noi_val and nb:
        mkt_data = nb.get("mkt", {})
        est_rent = mkt_data.get("rent", 2000)
        noi_val = est_rent * 12 * 0.60

    ica = income_approach(noi_val, market_cap or 5.0)

    with vc2:
        st.markdown('<div class="card"><div class="card-title">Income Approach</div>', unsafe_allow_html=True)
        if ica:
            st.markdown('<div style="text-align:center;padding:0.5rem 0;">'
                '<div style="font-size:0.6rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;">Indicated Value</div>'
                '<div style="font-size:1.6rem;font-weight:800;color:var(--navy);">{}</div>'
                '<div style="font-size:0.7rem;color:var(--slate-400);">NOI {} / Cap {:.1f}%</div>'
                '</div>'.format(format_currency(ica["indicated_value"]), format_currency(ica["noi"]), ica["cap_rate"]),
                unsafe_allow_html=True)
            if ica.get("scenarios"):
                rows = ""
                for s in ica["scenarios"]:
                    bold = " style='font-weight:700;'" if abs(s["cap"] - ica["cap_rate"]) < 0.1 else ""
                    rows += '<tr><td class="dk"{}>Cap {:.1f}%</td><td class="dv"{}>{}</td></tr>'.format(bold, s["cap"], bold, format_currency(s["value"]))
                st.markdown('<table class="dtable">{}</table>'.format(rows), unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warn">Income data needed. Go to Financial tab.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    land_psf = 80
    construction_psf = 200
    if nb_name:
        lc_data = get_land_comps(nb_name)
        if lc_data:
            psfs = [c.get("psf_land", 0) for c in lc_data if c.get("psf_land")]
            if psfs:
                land_psf = int(sum(psfs) / len(psfs))
        dev_data = get_dev_recommendation(nb_name)
        if dev_data and dev_data.get("construction", {}).get("cost_psf"):
            cost_str = dev_data["construction"]["cost_psf"].replace("$", "").replace(",", "")
            parts = cost_str.split("-")
            if len(parts) == 2:
                try:
                    construction_psf = (int(parts[0]) + int(parts[1])) // 2
                except ValueError:
                    pass

    cca = cost_approach(subj_lot or 5000, land_psf, subj_sqft or 1200, construction_psf, subj_year or 1990)

    with vc3:
        st.markdown('<div class="card"><div class="card-title">Cost Approach</div>', unsafe_allow_html=True)
        if cca:
            st.markdown('<div style="text-align:center;padding:0.5rem 0;">'
                '<div style="font-size:0.6rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;">Indicated Value</div>'
                '<div style="font-size:1.6rem;font-weight:800;color:var(--navy);">{}</div>'
                '<div style="font-size:0.7rem;color:var(--slate-400);">Land + Replacement - Depreciation</div>'
                '</div>'.format(format_currency(cca["indicated_value"])),
                unsafe_allow_html=True)
            rows = ""
            rows += tr("Land Value", "{} x ${}/sf = {}".format(format_number(cca["land_sf"]), cca["land_psf"], format_currency(cca["land_value"])))
            rows += tr("Replacement Cost", "{} x ${}/sf = {}".format(format_number(cca["building_sf"]), cca["construction_psf"], format_currency(cca["replacement_cost"])))
            rows += tr("Depreciation", "{:.0f}% ({} yrs) = -{}".format(cca["depreciation_pct"], cca["age"], format_currency(cca["depreciation"])))
            st.markdown('<table class="dtable">{}</table>'.format(rows), unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warn">Need lot size and building area for cost approach.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Reconciliation
    prop_type = "residential"
    if parcel:
        lu = (parcel.get("LAND USE") or "").upper()
        if "VACANT" in lu:
            prop_type = "land"
        elif "MULTI" in lu:
            prop_type = "investment"
        elif "COMMERCIAL" in lu:
            prop_type = "commercial"

    val_rec = reconcile(sca, ica, cca, prop_type)

    if val_rec:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;padding:1rem 0;">'
            '<div style="font-size:0.6rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1.5px;">Reconciled Market Value</div>'
            '<div style="font-size:2.2rem;font-weight:800;color:var(--navy);">{}</div>'
            '<div style="font-size:0.68rem;color:var(--slate-400);margin-top:0.3rem;">Weighted by {} property type</div>'
            '</div>'.format(format_currency(val_rec["reconciled_value"]), val_rec["property_type"]),
            unsafe_allow_html=True)

        fig = go.Figure()
        labels = [b["approach"] for b in val_rec["breakdown"]]
        values = [b["value"] for b in val_rec["breakdown"]]
        weights = [b["weight"] for b in val_rec["breakdown"]]
        colors = ["#2563eb", "#3b82f6", "#60a5fa"]
        fig.add_trace(go.Bar(x=labels, y=values, marker_color=colors[:len(labels)],
            text=["{}  ({}%)".format(format_currency(v), int(w * 100)) for v, w in zip(values, weights)],
            textposition="outside",
            hovertemplate="%{x}<br>Value: %{y:$,.0f}<extra></extra>"))
        fig.add_hline(y=val_rec["reconciled_value"], line_dash="dash", line_color="#dc2626",
            annotation_text="Reconciled: {}".format(format_currency(val_rec["reconciled_value"])),
            annotation_position="top left")
        fig.update_layout(**_chart_layout("", 350, y_title="Value ($)"))
        st.plotly_chart(fig, use_container_width=True)

        for b in val_rec["breakdown"]:
            st.markdown(score_bar("{} ({}%)".format(b["approach"], int(b["weight"] * 100)),
                int(b["value"] / max(val_rec["reconciled_value"], 1) * 100)), unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-warn">Not enough data to reconcile value. Enter property details and financial assumptions first.</div>', unsafe_allow_html=True)

    if sca and sca.get("adjustments"):
        with st.expander("Comparable Adjustments Detail"):
            for a in sca["adjustments"]:
                icon_color = "var(--green)" if a["direction"] == "up" else "var(--red)"
                arrow = "+" if a["direction"] == "up" else ""
                st.markdown(
                    '<div style="padding:0.5rem 0;border-bottom:1px solid var(--slate-100);">'
                    '<div style="display:flex;justify-content:space-between;">'
                    '<span style="font-weight:600;font-size:0.82rem;color:var(--navy);">{}</span>'
                    '<span style="font-weight:700;font-size:0.82rem;color:{};">{}{:.1f}%</span>'
                    '</div>'
                    '<div style="font-size:0.75rem;color:var(--slate-500);margin-top:2px;">{}</div>'
                    '</div>'.format(a["factor"], icon_color, arrow, a["impact_pct"], a["detail"]),
                    unsafe_allow_html=True)


# ── TAB 8: Risk ────────────────────────────────────────────
with tabs[8]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="card-title">Risk Factors</div>', unsafe_allow_html=True)
        rows = ""
        if nb:
            flood_val = nb.get("flood", "N/A")
            flood_color = "var(--red)" if "VE" in str(flood_val) else ("var(--amber)" if "AE" in str(flood_val) else "var(--green)")
            rows += '<tr><td class="dk">Flood Zone</td><td class="dv" style="color:{};">{}</td></tr>'.format(flood_color, flood_val)
            rows += tr("Crime Index", "{}/100".format(nb.get("crime", "N/A")))
            rows += tr("School Rating", str(nb.get("school", "N/A")))
            oz_val = "Yes" if nb.get("oz") else "No"
            oz_color = "var(--green)" if nb.get("oz") else "var(--slate-500)"
            rows += '<tr><td class="dk">Opportunity Zone</td><td class="dv" style="color:{};">{}</td></tr>'.format(oz_color, oz_val)
            mkt = nb.get("mkt", {})
            inv_mo = mkt.get("inv_mo", 0)
            inv_color = "var(--green)" if inv_mo < 3 else ("var(--amber)" if inv_mo < 6 else "var(--red)")
            rows += '<tr><td class="dk">Inventory (months)</td><td class="dv" style="color:{};">{}</td></tr>'.format(inv_color, inv_mo)
            rows += tr("Vacancy Rate", "{}%".format(nb.get("demo", {}).get("vacancy", "N/A")))
        else:
            rows += tr("Flood Zone", "N/A")
            rows += tr("Crime Index", "N/A")
        st.markdown('<table class="dtable">{}</table></div>'.format(rows), unsafe_allow_html=True)

        if nb and nb.get("risks"):
            st.markdown('<div class="card"><div class="card-title">Key Risks</div><ul style="font-size:0.8rem;color:var(--slate-700);line-height:1.8;margin:0;padding-left:1rem;">', unsafe_allow_html=True)
            for r in nb["risks"]:
                st.markdown('<li>{}</li>'.format(r), unsafe_allow_html=True)
            st.markdown('</ul></div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="card-title">Nearby Amenities</div>', unsafe_allow_html=True)
        if st.session_state.pois is None and geo.get("lat"):
            with st.spinner("Fetching POIs..."):
                st.session_state.pois = fetch_pois(geo["lat"], geo["lon"])

        pois = st.session_state.pois or {}
        if pois:
            for cat, items in pois.items():
                n = len(items)
                st.markdown('<div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid var(--slate-100);font-size:0.8rem;">'
                            '<span style="color:var(--slate-500);">{}</span>'
                            '<span style="font-weight:600;color:var(--navy);">{} found</span></div>'.format(cat, n), unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-info">No POI data available. <span class="source-tag">DEMO</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">Risk Score</div>', unsafe_allow_html=True)
        risk_sc = scores.get("risk", 50)
        risk_color = "var(--green)" if risk_sc >= 70 else ("var(--amber)" if risk_sc >= 40 else "var(--red)")
        st.markdown(
            '<div style="text-align:center;padding:1rem;">'
            '<div style="font-size:2.5rem;font-weight:800;color:{};">{}</div>'
            '<div style="font-size:0.65rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;">Risk Score / 100</div>'
            '<div style="font-size:0.7rem;color:var(--slate-400);margin-top:0.5rem;">Higher = Lower Risk</div>'
            '</div>'.format(risk_color, risk_sc), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Risk radar chart
    if scores:
        fig = go.Figure()
        risk_cats = ["Location", "Market", "Financial", "Risk", "Data"]
        risk_vals = [scores.get("location", 0), scores.get("market", 0), scores.get("financial", 0), scores.get("risk", 0), scores.get("data_confidence", 0)]
        fig.add_trace(go.Scatterpolar(
            r=risk_vals + [risk_vals[0]],
            theta=risk_cats + [risk_cats[0]],
            fill="toself",
            fillcolor="rgba(37,99,235,0.15)",
            line=dict(color="#2563eb", width=2),
            hovertemplate="%{theta}: %{r}/100<extra></extra>",
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#e2e8f0"),
                        angularaxis=dict(gridcolor="#e2e8f0")),
            showlegend=False, height=350,
            margin=dict(l=40, r=40, t=30, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", size=12, color="#475569"),
        )
        st.plotly_chart(fig, use_container_width=True)


# ── TAB 9: AI Summary ─────────────────────────────────────
with tabs[9]:
    st.markdown('<div class="card"><div class="card-title">AI Investment Summary <span class="source-tag">AI GENERATED</span></div>', unsafe_allow_html=True)
    summary_html = generate_summary(
        st.session_state.address, geo, nb_name, nb,
        scores, st.session_state.financials, records
    )
    st.markdown(summary_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── TAB 10: Best Recommendation ──────────────────────────
with tabs[10]:
    val_rec_data = None
    if 'val_rec' in dir() and val_rec:
        val_rec_data = val_rec

    comps_cnt = len(val_comps) if 'val_comps' in dir() else 0
    rec = generate_recommendation(
        geo, nb_name, nb, parcel, scores,
        st.session_state.financials, val_rec_data, comps_cnt
    )

    # Verdict
    st.markdown(
        '<div class="verdict-box" style="border-color:{};">'
        '<div class="verdict-label">Investment Verdict</div>'
        '<div class="verdict-value" style="color:{};">{}</div>'
        '<div class="verdict-sub">Overall Score: {}/100 | Strategy: {}</div>'
        '</div>'.format(rec["verdict_color"], rec["verdict_color"], rec["verdict"], rec["overall"], rec["strategy"]),
        unsafe_allow_html=True,
    )

    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown('<div class="card"><div class="card-title">Highest & Best Use</div>'
            '<div style="font-size:1.1rem;font-weight:700;color:var(--navy);margin:0.3rem 0;">{}</div>'
            '<div style="font-size:0.8rem;color:var(--slate-500);">Recommended Strategy: <b>{}</b></div>'
            '</div>'.format(rec["hbu"], rec["strategy"]),
            unsafe_allow_html=True)
    with rc2:
        st.markdown('<div class="card"><div class="card-title">Financial Scenario</div>'
            '<div style="font-size:1.1rem;font-weight:700;color:var(--navy);margin:0.3rem 0;">{} Scenario Recommended</div>'
            '<div style="font-size:0.8rem;color:var(--slate-500);">{}</div>'
            '<div style="font-size:0.75rem;color:var(--slate-400);margin-top:0.3rem;">Risk-Adjusted Return: {:.1f}%</div>'
            '</div>'.format(rec["scenario_rec"], rec["scenario_detail"], rec["risk_adj_return"]),
            unsafe_allow_html=True)

    # Reasons & Red Flags
    rf1, rf2 = st.columns(2)
    with rf1:
        st.markdown('<div class="card"><div class="card-title">Top 5 Reasons For</div>', unsafe_allow_html=True)
        for i, (title, detail) in enumerate(rec["reasons"][:5], 1):
            st.markdown(
                '<div class="ranked-item">'
                '<div class="ranked-num" style="background:#16a34a;">{}</div>'
                '<div class="ranked-body"><div class="ranked-title">{}</div>'
                '<div class="ranked-detail">{}</div></div></div>'.format(i, title, detail),
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with rf2:
        st.markdown('<div class="card"><div class="card-title">Top Red Flags</div>', unsafe_allow_html=True)
        for i, (title, detail) in enumerate(rec["red_flags"][:5], 1):
            st.markdown(
                '<div class="ranked-item">'
                '<div class="ranked-num" style="background:#dc2626;">{}</div>'
                '<div class="ranked-body"><div class="ranked-title">{}</div>'
                '<div class="ranked-detail">{}</div></div></div>'.format(i, title, detail),
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Missing Data & DD
    md1, md2 = st.columns(2)
    with md1:
        st.markdown('<div class="card"><div class="card-title">Missing Data</div><ul style="font-size:0.8rem;color:var(--slate-700);line-height:1.8;margin:0;padding-left:1rem;">', unsafe_allow_html=True)
        for m in rec["missing"]:
            st.markdown('<li>{}</li>'.format(m), unsafe_allow_html=True)
        st.markdown('</ul></div>', unsafe_allow_html=True)

    with md2:
        st.markdown('<div class="card"><div class="card-title">Due Diligence Steps</div><ol style="font-size:0.8rem;color:var(--slate-700);line-height:1.8;margin:0;padding-left:1rem;">', unsafe_allow_html=True)
        for step in rec["dd_steps"]:
            st.markdown('<li>{}</li>'.format(step), unsafe_allow_html=True)
        st.markdown('</ol></div>', unsafe_allow_html=True)

    # Investment Memo
    st.markdown('<div class="card"><div class="card-title">Investment Memo</div>'
        '<p style="font-size:0.85rem;color:var(--slate-700);line-height:1.7;margin:0;">{}</p>'
        '</div>'.format(rec["memo"]),
        unsafe_allow_html=True)

    # Investor Take
    st.markdown(
        '<div class="card" style="border-left:4px solid {};">'
        '<div class="card-title">What I Would Do as the Investor</div>'
        '<p style="font-size:0.85rem;color:var(--navy);line-height:1.7;font-style:italic;margin:0;">&ldquo;{}&rdquo;</p>'
        '</div>'.format(rec["verdict_color"], rec["investor_take"]),
        unsafe_allow_html=True)


# ── TAB 11: Export ─────────────────────────────────────────
with tabs[11]:
    report_data = build_report_data(geo, nb_name, nb, records, parcel)

    rec_for_export = None
    if 'rec' in dir():
        rec_for_export = rec

    dp_for_export = None
    if 'dp' in dir():
        dp_for_export = dp

    val_rec_export = None
    if 'val_rec' in dir() and val_rec:
        val_rec_export = val_rec

    st.markdown('<div class="card"><div class="card-title">Download Report</div>'
        '<div style="font-size:0.82rem;color:var(--slate-500);margin-bottom:0.8rem;">Export the full analysis in your preferred format.</div>',
        unsafe_allow_html=True)

    ec1, ec2, ec3, ec4 = st.columns(4)
    with ec1:
        csv_data = export_csv(report_data, st.session_state.address)
        st.download_button("CSV", csv_data, file_name="patton_report.csv", mime="text/csv", use_container_width=True)
    with ec2:
        json_data = export_json(report_data, st.session_state.address)
        st.download_button("JSON", json_data, file_name="patton_report.json", mime="application/json", use_container_width=True)
    with ec3:
        md_data = export_markdown(report_data, st.session_state.address, scores, st.session_state.financials, nb_name)
        st.download_button("Markdown", md_data, file_name="patton_report.md", mime="text/markdown", use_container_width=True)
    with ec4:
        pro_html = export_professional_html(
            st.session_state.address, geo, nb_name, nb, parcel,
            scores, st.session_state.financials, rec_for_export,
            dp_for_export, val_rec_export,
        )
        st.download_button("HTML Report", pro_html, file_name="patton_report.html", mime="text/html", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Report Preview (Markdown)"):
        preview_md = export_markdown(report_data, st.session_state.address, scores, st.session_state.financials, nb_name)
        st.code(preview_md, language="markdown")
