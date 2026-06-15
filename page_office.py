import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from utils.style import inject_css, kpi, tr, LOGO_B64
from utils.buildings_inventory import get_all_buildings, get_building, get_vacant_suites, get_portfolio_summary
from utils.property_data import format_currency
import math


STEP_NAMES = ["Budget", "Size", "Building", "Suite"]
AVAIL_STATUSES = ("vacant", "expired")


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def _progress_bar(current, choices):
    html = '<div style="margin:0.8rem 0 1.2rem;overflow-x:auto;">'
    html += '<div style="display:flex;align-items:center;gap:0;">'
    for i, name in enumerate(STEP_NAMES):
        if i < current:
            bg = "#16a34a"; fg = "white"; border = "#16a34a"
        elif i == current:
            bg = "#2563eb"; fg = "white"; border = "#2563eb"
        else:
            bg = "#f1f5f9"; fg = "#94a3b8"; border = "#e2e8f0"

        choice_text = ""
        if i < len(choices) and choices[i]:
            c_color = "rgba(255,255,255,0.85)" if i <= current else "#94a3b8"
            choice_text = '<div style="font-size:0.6rem;color:{};margin-top:2px;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{}</div>'.format(c_color, choices[i])

        html += (
            '<div style="display:flex;flex-direction:column;align-items:center;min-width:110px;">'
            '<div style="width:36px;height:36px;border-radius:50%;background:{bg};color:{fg};border:2px solid {bd};'
            'display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;">'
            '{num}</div>'
            '<div style="font-size:0.65rem;font-weight:600;color:{lc};margin-top:4px;letter-spacing:0.3px;">{name}</div>'
            '{ct}</div>'
        ).format(bg=bg, fg=fg, bd=border,
                 num="&#10003;" if i < current else str(i + 1),
                 lc=fg if i == current else ("#16a34a" if i < current else "#94a3b8"),
                 name=name, ct=choice_text)

        if i < len(STEP_NAMES) - 1:
            arrow_color = "#16a34a" if i < current else ("#2563eb" if i == current else "#e2e8f0")
            html += '<div style="flex:1;height:3px;background:{};min-width:40px;margin:0 4px;border-radius:2px;margin-bottom:{}px;"></div>'.format(
                arrow_color, 20 if any(choices) else 0)

    html += '</div></div>'
    return html


def _amenities_badges(amenities):
    icons = {
        "Lobby": "&#127970;", "Parking garage": "&#128663;", "Garage": "&#128663;",
        "Surface parking": "&#128663;", "Security": "&#128274;", "Fitness center": "&#127947;",
        "Conference room": "&#128221;", "Conference facility": "&#128221;", "Cafe": "&#9749;",
        "On-site management": "&#128100;", "Near Metrorail": "&#128646;", "Highway access": "&#128739;",
    }
    items = ""
    for a in amenities:
        icon = icons.get(a, "&#10003;")
        items += '<span style="display:inline-flex;align-items:center;gap:3px;background:var(--slate-50);border:1px solid var(--slate-200);border-radius:6px;padding:3px 8px;font-size:0.68rem;color:var(--slate-700);white-space:nowrap;">{} {}</span>'.format(icon, a)
    return '<div style="display:flex;gap:0.4rem;flex-wrap:wrap;margin-top:0.5rem;">{}</div>'.format(items)


def _parking_card(b):
    pd_info = b.get("parking_details") or {}
    if not pd_info:
        return ""
    covered = "Covered" if pd_info.get("covered") else "Uncovered"
    ev = '<span class="badge badge-green" style="margin-left:0.3rem;">EV Charging</span>' if pd_info.get("ev_charging") else ""
    return (
        '<div style="background:var(--slate-50);border:1px solid var(--slate-200);border-radius:8px;padding:0.6rem 0.8rem;margin-top:0.5rem;">'
        '<div style="font-size:0.65rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:0.3rem;">&#128663; Parking</div>'
        '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.4rem;font-size:0.78rem;">'
        '<div><span style="color:var(--slate-400);font-size:0.65rem;">Type</span><br><b style="color:var(--navy);">{}</b></div>'
        '<div><span style="color:var(--slate-400);font-size:0.65rem;">Spaces</span><br><b style="color:var(--navy);">{}</b></div>'
        '<div><span style="color:var(--slate-400);font-size:0.65rem;">Ratio</span><br><b style="color:var(--navy);">{}</b></div>'
        '</div>'
        '<div style="font-size:0.65rem;color:var(--slate-500);margin-top:0.3rem;">{}{}</div>'
        '</div>'
    ).format(pd_info.get("type", "N/A"), pd_info.get("spaces", "N/A"),
             pd_info.get("ratio", "N/A"), covered, ev)


def _rooftop_card(b):
    rt = b.get("rooftop")
    if not rt:
        return ""
    items = "".join('<li style="font-size:0.75rem;color:var(--slate-600);line-height:1.5;">{}</li>'.format(f) for f in rt.get("features", []))
    return (
        '<div style="background:linear-gradient(135deg,var(--blue-50),var(--green-50));border:1px solid var(--slate-200);border-radius:8px;padding:0.6rem 0.8rem;margin-top:0.5rem;">'
        '<div style="font-size:0.65rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:0.3rem;">&#127749; Rooftop</div>'
        '<ul style="margin:0;padding-left:1rem;">{}</ul>'
        '</div>'
    ).format(items)


def _floor_plan_svg(suite_name, sf, suite_type="office"):
    w = min(max(int(math.sqrt(sf) * 1.2), 80), 200)
    h = min(max(int(sf / max(w, 1) * 0.8), 60), 150)
    rooms = []
    if sf < 2000:
        rooms = [("Open Office", 0, 0, w, int(h * 0.7)),
                 ("Kitchenette", 0, int(h * 0.7), int(w * 0.4), int(h * 0.3)),
                 ("WC", int(w * 0.4), int(h * 0.7), int(w * 0.6), int(h * 0.3))]
    elif sf < 5000:
        rooms = [("Reception", 0, 0, int(w * 0.35), int(h * 0.4)),
                 ("Office 1", int(w * 0.35), 0, int(w * 0.65), int(h * 0.4)),
                 ("Open Area", 0, int(h * 0.4), w, int(h * 0.35)),
                 ("Kitchen", 0, int(h * 0.75), int(w * 0.3), int(h * 0.25)),
                 ("Conf Room", int(w * 0.3), int(h * 0.75), int(w * 0.4), int(h * 0.25)),
                 ("WC", int(w * 0.7), int(h * 0.75), int(w * 0.3), int(h * 0.25))]
    else:
        rooms = [("Reception", 0, 0, int(w * 0.3), int(h * 0.35)),
                 ("Exec Office", int(w * 0.3), 0, int(w * 0.35), int(h * 0.35)),
                 ("Conf Room", int(w * 0.65), 0, int(w * 0.35), int(h * 0.35)),
                 ("Open Floor", 0, int(h * 0.35), w, int(h * 0.35)),
                 ("Kitchen", 0, int(h * 0.7), int(w * 0.25), int(h * 0.3)),
                 ("Break Room", int(w * 0.25), int(h * 0.7), int(w * 0.25), int(h * 0.3)),
                 ("Server", int(w * 0.5), int(h * 0.7), int(w * 0.2), int(h * 0.3)),
                 ("WC", int(w * 0.7), int(h * 0.7), int(w * 0.3), int(h * 0.3))]

    pad = 20
    svg_w = w + pad * 2
    svg_h = h + pad * 2 + 24
    colors = ["#eff6ff", "#f0fdf4", "#fffbeb", "#fef2f2", "#f5f3ff", "#ecfeff", "#fdf4ff", "#fff7ed"]
    svg = '<svg viewBox="0 0 {} {}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:320px;height:auto;">'.format(svg_w, svg_h)
    svg += '<text x="{}" y="14" text-anchor="middle" font-size="9" font-weight="700" fill="#0f172a" font-family="Inter,sans-serif">Suite {} &mdash; {:,} sqft</text>'.format(svg_w // 2, suite_name, sf)
    svg += '<rect x="{}" y="{}" width="{}" height="{}" fill="white" stroke="#94a3b8" stroke-width="1.5" rx="3"/>'.format(pad, pad + 16, w, h)
    for idx, (name, rx, ry, rw, rh) in enumerate(rooms):
        if rw <= 0 or rh <= 0:
            continue
        fill = colors[idx % len(colors)]
        svg += '<rect x="{}" y="{}" width="{}" height="{}" fill="{}" stroke="#cbd5e1" stroke-width="0.7"/>'.format(
            pad + rx, pad + 16 + ry, rw, rh, fill)
        font_size = max(5, min(7, rw // 8))
        tx = pad + rx + rw // 2
        ty = pad + 16 + ry + rh // 2 + 2
        svg += '<text x="{}" y="{}" text-anchor="middle" font-size="{}" fill="#475569" font-family="Inter,sans-serif">{}</text>'.format(tx, ty, font_size, name)
    svg += '<rect x="{}" y="{}" width="8" height="3" fill="#2563eb" rx="1"/>'.format(pad, pad + 16 + h // 2)
    svg += '<text x="{}" y="{}" font-size="4" fill="#2563eb" font-family="Inter,sans-serif">Entry</text>'.format(pad + 1, pad + 16 + h // 2 - 2)
    svg += '</svg>'
    return svg


def render_office_page():
    inject_css()

    defaults = [("os_step", 0), ("os_building", None),
                ("os_min_sf", 0), ("os_max_sf", 50000),
                ("os_budget_max", 100)]
    for k, v in defaults:
        if k not in st.session_state:
            st.session_state[k] = v

    summary = get_portfolio_summary()
    buildings = get_all_buildings()
    all_available = get_vacant_suites()

    # ── Sidebar ──
    with st.sidebar:
        logo_html = ""
        if LOGO_B64:
            logo_html = '<img src="data:image/png;base64,{}" style="height:48px;margin-bottom:0.5rem;">'.format(LOGO_B64)
        st.markdown(
            '<div style="text-align:center;padding:1rem 0 0.5rem;">'
            '{}'
            '<div style="color:#fff;font-size:1.1rem;font-weight:700;letter-spacing:1px;">PATTON</div>'
            '<div style="color:#64748b;font-size:0.58rem;letter-spacing:2px;text-transform:uppercase;margin-top:2px;">Office Suite Finder</div>'
            '</div>'.format(logo_html),
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:0.8rem 0;"></div>', unsafe_allow_html=True)

        if st.button("Back to Home", use_container_width=True, key="os_home"):
            st.session_state["app_mode"] = "home"
            st.rerun()

        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:0.6rem 0;"></div>', unsafe_allow_html=True)

        st.markdown(
            '<div style="text-align:center;margin:0.3rem 0;">'
            '<div style="color:#94a3b8;font-size:0.55rem;letter-spacing:2px;text-transform:uppercase;">Portfolio</div>'
            '<div style="color:#fff;font-size:2rem;font-weight:800;">{}</div>'
            '<div style="color:#64748b;font-size:0.62rem;">Buildings &mdash; {}% occupied</div>'
            '</div>'.format(summary["buildings"], summary["occupancy"]),
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align:center;margin:0.3rem 0;">'
            '<div style="color:#16a34a;font-size:1.6rem;font-weight:800;">{}</div>'
            '<div style="color:#64748b;font-size:0.62rem;">available suites &mdash; {:,} sqft</div>'
            '</div>'.format(summary["vacant_suites"], summary["vacant_rsf"]),
            unsafe_allow_html=True,
        )

        st.markdown('<div style="height:1px;background:rgba(255,255,255,0.08);margin:0.6rem 0;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#94a3b8;font-size:0.55rem;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.3rem;">Client Criteria</div>', unsafe_allow_html=True)

        prefs = []
        if st.session_state.os_step > 0:
            prefs.append(("Max Rate", "${}/sqft".format(st.session_state.os_budget_max)))
        if st.session_state.os_step > 1:
            mn = st.session_state.os_min_sf
            mx = st.session_state.os_max_sf
            prefs.append(("Size", "Any" if (mn == 0 and mx >= 50000) else "{:,}-{:,} sf".format(mn, mx)))
        if st.session_state.os_step > 2 and st.session_state.os_building:
            bld = get_building(st.session_state.os_building)
            if bld:
                prefs.append(("Building", bld["name"]))

        if prefs:
            for label, val in prefs:
                st.markdown(
                    '<div style="display:flex;justify-content:space-between;padding:0.2rem 0;border-bottom:1px solid rgba(255,255,255,0.06);font-size:0.72rem;">'
                    '<span style="color:#64748b;">{}</span>'
                    '<span style="color:#e2e8f0;font-weight:600;">{}</span></div>'.format(label, val),
                    unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.72rem;color:#475569;">No criteria set yet</div>', unsafe_allow_html=True)

    # ── Header ──
    hdr_logo = ""
    if LOGO_B64:
        hdr_logo = '<img src="data:image/png;base64,{}">'.format(LOGO_B64)

    st.markdown(
        '<div class="app-header">'
        '<div class="hd-left">{}<div><div class="hd-title">PATTON</div><div class="hd-sub">OFFICE SUITE FINDER</div></div></div>'
        '<div style="display:flex;gap:0.5rem;align-items:center;">'
        '<span class="badge badge-blue">Tenant Rep</span>'
        '<span class="badge badge-green">{} Available Suites</span></div>'
        '</div>'.format(hdr_logo, summary["vacant_suites"]),
        unsafe_allow_html=True,
    )

    step = st.session_state.os_step

    choices = ["", "", "", ""]
    if step > 0:
        choices[0] = "Max ${}/sf".format(st.session_state.os_budget_max)
    if step > 1:
        mn = st.session_state.os_min_sf
        mx = st.session_state.os_max_sf
        choices[1] = "Any" if (mn == 0 and mx >= 50000) else "{:,}-{:,}sf".format(mn, mx)
    if step > 2 and st.session_state.os_building:
        bld_obj = get_building(st.session_state.os_building)
        choices[2] = bld_obj["name"] if bld_obj else ""

    st.markdown(_progress_bar(step, choices), unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # STEP 0: Budget
    # ══════════════════════════════════════════════════════════
    if step == 0:
        st.markdown(
            '<div class="verdict-box">'
            '<div class="verdict-label">Step 1 of 4</div>'
            '<div class="verdict-value" style="color:var(--navy);">What is the tenant\'s budget?</div>'
            '<div class="verdict-sub">Set the maximum price per sqft/year the tenant is willing to pay</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        rates = sorted(set(s["asking_rate"] for s in all_available if s["asking_rate"]))
        min_rate = int(min(rates)) if rates else 20
        max_rate = int(max(rates)) + 5 if rates else 60

        if rates:
            avg_rate = sum(rates) / len(rates)
            kpi_items = []
            kpi_items.append(kpi("Available Suites", str(len(all_available)), "across {} buildings".format(summary["buildings"])))
            kpi_items.append(kpi("Lowest Rate", "${:.0f}/sqft".format(min(rates)), "Per year"))
            kpi_items.append(kpi("Average Rate", "${:.0f}/sqft".format(avg_rate), "Per year"))
            kpi_items.append(kpi("Highest Rate", "${:.0f}/sqft".format(max(rates)), "Per year"))
            st.markdown('<div class="kpi-grid">{}</div>'.format("".join(kpi_items)), unsafe_allow_html=True)

        if all_available:
            rate_buckets = {}
            for s in all_available:
                r = s["asking_rate"]
                if r:
                    bucket = "${}-${}".format(int(r // 5) * 5, int(r // 5) * 5 + 5)
                    rate_buckets[bucket] = rate_buckets.get(bucket, 0) + 1
            if rate_buckets:
                st.markdown('<div class="card"><div class="card-title">Rate Distribution</div>', unsafe_allow_html=True)
                fig = go.Figure()
                fig.add_trace(go.Bar(x=list(rate_buckets.keys()), y=list(rate_buckets.values()),
                    marker_color="#2563eb",
                    hovertemplate="Rate: %{x}/sqft<br>Suites: %{y}<extra></extra>"))
                fig.update_layout(height=200, margin=dict(l=30, r=10, t=10, b=30),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(gridcolor="#e2e8f0"), yaxis=dict(gridcolor="#e2e8f0"),
                    font=dict(family="Inter", size=11, color="#475569"))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">Select Maximum Budget</div>', unsafe_allow_html=True)
        budget_options = [
            ("$35/sqft", 35), ("$40/sqft", 40), ("$45/sqft", 45), ("No Limit", max_rate),
        ]
        bcols = st.columns(len(budget_options))
        for i, (label, bmx) in enumerate(budget_options):
            matching = [s for s in all_available if s["asking_rate"] and s["asking_rate"] <= bmx]
            with bcols[i]:
                st.markdown(
                    '<div style="text-align:center;padding:0.4rem 0;">'
                    '<div style="font-size:0.95rem;font-weight:700;color:var(--navy);">{}</div>'
                    '<div style="font-size:0.75rem;font-weight:600;color:#16a34a;margin-top:0.2rem;">{} suites</div>'
                    '</div>'.format(label, len(matching)),
                    unsafe_allow_html=True)
                if st.button("Select", use_container_width=True, key="bgt_{}".format(i)):
                    st.session_state.os_budget_max = bmx
                    st.session_state.os_step = 1
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("Custom Max Rate"):
            custom_max = st.slider("Max rate ($/sqft/yr)", min_rate, max_rate, max_rate, key="budget_slider")
            matching_custom = [s for s in all_available if s["asking_rate"] and s["asking_rate"] <= custom_max]
            st.markdown('{} suites at or below ${}/sqft'.format(len(matching_custom), custom_max))
            if st.button("Apply", use_container_width=True, key="bgt_custom"):
                st.session_state.os_budget_max = custom_max
                st.session_state.os_step = 1
                st.rerun()

    # ══════════════════════════════════════════════════════════
    # STEP 1: Size
    # ══════════════════════════════════════════════════════════
    elif step == 1:
        bgt_max = st.session_state.os_budget_max
        budget_suites = [s for s in all_available if s["asking_rate"] and s["asking_rate"] <= bgt_max]

        st.markdown(
            '<div class="verdict-box">'
            '<div class="verdict-label">Step 2 of 4</div>'
            '<div class="verdict-value" style="color:var(--navy);">How much space?</div>'
            '<div class="verdict-sub">{} suites available at max ${}/sqft/yr</div>'
            '</div>'.format(len(budget_suites), bgt_max),
            unsafe_allow_html=True,
        )

        if st.button("< Back to Budget", key="back_to_bgt"):
            st.session_state.os_step = 0
            st.rerun()

        if budget_suites:
            sizes = [(s.get("boma_rsf") or s.get("rsf", 0)) for s in budget_suites]
            kpi_items = []
            kpi_items.append(kpi("Suites", str(len(budget_suites)), "in budget"))
            kpi_items.append(kpi("Smallest", "{:,} sqft".format(min(sizes)), ""))
            kpi_items.append(kpi("Largest", "{:,} sqft".format(max(sizes)), ""))
            kpi_items.append(kpi("Total", "{:,} sqft".format(sum(sizes)), "available"))
            st.markdown('<div class="kpi-grid">{}</div>'.format("".join(kpi_items)), unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">Select Size Range</div>', unsafe_allow_html=True)
        size_options = [
            ("Small", 0, 2000, "Under 2,000 sqft"),
            ("Medium", 2000, 5000, "2,000 - 5,000 sqft"),
            ("Large", 5000, 10000, "5,000 - 10,000 sqft"),
            ("Very Large", 10000, 50000, "10,000+ sqft"),
            ("Any Size", 0, 50000, "Show all"),
        ]
        scols = st.columns(len(size_options))
        for i, (label, mn, mx, desc) in enumerate(size_options):
            matching = [s for s in budget_suites if mn <= (s.get("boma_rsf") or s.get("rsf", 0)) <= mx]
            with scols[i]:
                st.markdown(
                    '<div style="text-align:center;padding:0.3rem 0;">'
                    '<div style="font-size:0.85rem;font-weight:700;color:var(--navy);">{}</div>'
                    '<div style="font-size:0.68rem;color:var(--slate-500);">{}</div>'
                    '<div style="font-size:0.72rem;font-weight:600;color:#16a34a;margin-top:0.2rem;">{} suites</div>'
                    '</div>'.format(label, desc, len(matching)),
                    unsafe_allow_html=True)
                if st.button("Select", use_container_width=True, key="size_{}".format(i), disabled=len(matching) == 0):
                    st.session_state.os_min_sf = mn
                    st.session_state.os_max_sf = mx
                    st.session_state.os_step = 2
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # STEP 2: Building
    # ══════════════════════════════════════════════════════════
    elif step == 2:
        bgt_max = st.session_state.os_budget_max
        min_sf = st.session_state.os_min_sf
        max_sf = st.session_state.os_max_sf

        size_label = "Any size"
        if min_sf == 0 and max_sf == 2000:
            size_label = "< 2,000 sqft"
        elif min_sf == 2000 and max_sf == 5000:
            size_label = "2k-5k sqft"
        elif min_sf == 5000 and max_sf == 10000:
            size_label = "5k-10k sqft"
        elif min_sf == 10000:
            size_label = "10k+ sqft"

        st.markdown(
            '<div class="verdict-box">'
            '<div class="verdict-label">Step 3 of 4</div>'
            '<div class="verdict-value" style="color:var(--navy);">Choose a Building</div>'
            '<div class="verdict-sub">Max ${}/sqft &mdash; {} &mdash; Showing buildings with matching suites</div>'
            '</div>'.format(bgt_max, size_label),
            unsafe_allow_html=True,
        )

        if st.button("< Back to Size", key="back_to_size"):
            st.session_state.os_step = 1
            st.rerun()

        any_match = False
        for b in buildings:
            vac_suites = [s for s in b["suites"] if s["status"] in AVAIL_STATUSES
                          and s.get("asking_rate") and s["asking_rate"] <= bgt_max
                          and min_sf <= (s.get("boma_rsf") or s.get("rsf", 0)) <= max_sf]
            if not vac_suites:
                continue
            any_match = True

            s_rates = [s["asking_rate"] for s in vac_suites]
            s_sizes = [(s.get("boma_rsf") or s.get("rsf", 0)) for s in vac_suites]

            rt = b.get("rooftop")
            rt_badge = '<span class="badge badge-green">Rooftop</span>' if rt else ""
            pd_info = b.get("parking_details") or {}
            ev_badge = '<span class="badge badge-green">EV</span>' if pd_info.get("ev_charging") else ""

            st.markdown(
                '<div class="card">'
                '<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                '<div>'
                '<div class="card-title" style="margin-bottom:0.15rem;">{name}</div>'
                '<div style="font-size:0.78rem;color:var(--slate-500);">{addr}</div>'
                '</div>'
                '<div style="text-align:right;">'
                '<div style="font-size:1.4rem;font-weight:800;color:#16a34a;">{vac}</div>'
                '<div style="font-size:0.6rem;color:var(--slate-400);">matching suites</div>'
                '</div></div>'
                '<div style="display:flex;gap:0.4rem;margin-top:0.5rem;flex-wrap:wrap;">'
                '<span class="badge badge-blue">Class {cls}</span>'
                '<span class="badge badge-blue">{rsf:,} sqft</span>'
                '<span class="badge badge-amber">{fl} fl</span>'
                '<span class="badge badge-amber">{parking}</span>'
                '{rt}{ev}</div>'
                '<div style="font-size:0.72rem;color:var(--slate-400);margin-top:0.4rem;">{desc}</div>'
                '<div style="margin-top:0.5rem;font-size:0.75rem;color:var(--slate-500);">'
                'Sizes: {minsf:,} - {maxsf:,} sqft &nbsp;|&nbsp; Rates: ${minr:.0f} - ${maxr:.0f}/sqft/yr'
                '</div>'
                '{amenities}'
                '{parking_card}'
                '{rooftop_card}'
                '</div>'.format(
                    name=b["name"], addr=b["address"],
                    vac=len(vac_suites), cls=b["building_class"], rsf=b["building_rsf"],
                    fl=b["floors"], parking=b.get("parking", "N/A"),
                    rt=rt_badge, ev=ev_badge, desc=b["description"],
                    minsf=min(s_sizes), maxsf=max(s_sizes),
                    minr=min(s_rates), maxr=max(s_rates),
                    amenities=_amenities_badges(b["amenities"]),
                    parking_card=_parking_card(b),
                    rooftop_card=_rooftop_card(b),
                ),
                unsafe_allow_html=True,
            )

            if st.button("Select {}".format(b["name"]), use_container_width=True, key="bld_{}".format(b["id"])):
                st.session_state.os_building = b["id"]
                st.session_state.os_step = 3
                st.rerun()

        if not any_match:
            st.markdown('<div class="alert-warn">No buildings have matching suites. Try adjusting budget or size.</div>', unsafe_allow_html=True)

        # ── Interactive map: click a location to pick the exact office lot ──
        st.markdown(
            '<div class="card"><div class="card-title">Pick a Lot on the Map</div>'
            '<div style="font-size:0.76rem;color:var(--slate-500);margin-bottom:0.5rem;">'
            'Click a building pin on the map. If several office lots sit close together, '
            'every nearby lot is listed below so you can choose the exact one.</div>',
            unsafe_allow_html=True,
        )
        mp = folium.Map(location=[25.78, -80.30], zoom_start=11, tiles="CartoDB positron")
        for b in buildings:
            vac = sum(1 for s in b["suites"] if s["status"] in AVAIL_STATUSES
                      and s.get("asking_rate") and s["asking_rate"] <= bgt_max
                      and min_sf <= (s.get("boma_rsf") or s.get("rsf", 0)) <= max_sf)
            color = "#16a34a" if vac > 0 else "#94a3b8"
            popup_html = "<b>{}</b><br>{}<br>{} matching suites".format(b["name"], b["address"], vac)
            folium.CircleMarker(
                [b["lat"], b["lon"]], radius=11, color="#ffffff", weight=2,
                fill=True, fill_color=color, fill_opacity=0.95,
                tooltip=b["name"],
                popup=folium.Popup(popup_html, max_width=250),
            ).add_to(mp)
        map_out = st_folium(mp, width=None, height=360,
                            returned_objects=["last_object_clicked", "last_clicked"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Resolve the clicked point to nearby office lots and propose each one.
        click = None
        if map_out:
            click = map_out.get("last_object_clicked") or map_out.get("last_clicked")
        if click and click.get("lat") is not None:
            clat, clon = click["lat"], click["lng"]
            ranked = sorted(buildings, key=lambda b: _haversine_km(clat, clon, b["lat"], b["lon"]))
            nearby = [b for b in ranked if _haversine_km(clat, clon, b["lat"], b["lon"]) <= 0.4]
            if not nearby and ranked:
                nearby = ranked[:1]

            st.markdown(
                '<div style="font-size:0.95rem;font-weight:800;color:var(--navy);margin:0.8rem 0 0.4rem;">'
                '{} lot{} near your click</div>'.format(len(nearby), "s" if len(nearby) != 1 else ""),
                unsafe_allow_html=True,
            )
            for b in nearby:
                vac_suites = [s for s in b["suites"] if s["status"] in AVAIL_STATUSES
                              and s.get("asking_rate") and s["asking_rate"] <= bgt_max
                              and min_sf <= (s.get("boma_rsf") or s.get("rsf", 0)) <= max_sf]
                dist_m = int(_haversine_km(clat, clon, b["lat"], b["lon"]) * 1000)
                rates = [s["asking_rate"] for s in vac_suites]
                rate_txt = "${:.0f}-${:.0f}/sf".format(min(rates), max(rates)) if rates else "no match in budget"
                with st.container(border=True):
                    st.markdown(
                        '<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                        '<div><div style="font-size:1rem;font-weight:800;color:var(--navy);">{name}</div>'
                        '<div style="font-size:0.74rem;color:var(--slate-500);">{addr}</div>'
                        '<div style="font-size:0.68rem;color:var(--slate-400);margin-top:0.2rem;">'
                        '~{dist} m from click &middot; Class {cls} &middot; {fl} floors</div></div>'
                        '<div style="text-align:right;"><div style="font-size:1.3rem;font-weight:800;color:{vc};">{vac}</div>'
                        '<div style="font-size:0.58rem;color:var(--slate-400);">matching suites</div>'
                        '<div style="font-size:0.68rem;color:var(--slate-500);margin-top:0.2rem;">{rate}</div></div>'
                        '</div>'.format(
                            name=b["name"], addr=b["address"], dist=dist_m,
                            cls=b["building_class"], fl=b["floors"],
                            vac=len(vac_suites), vc="#16a34a" if vac_suites else "#94a3b8",
                            rate=rate_txt),
                        unsafe_allow_html=True,
                    )
                    if st.button("Select this lot \u2192", use_container_width=True,
                                 key="lot_pick_{}".format(b["id"]), type="primary",
                                 disabled=len(vac_suites) == 0):
                        st.session_state.os_building = b["id"]
                        st.session_state.os_step = 3
                        st.rerun()

    # ══════════════════════════════════════════════════════════
    # STEP 3: Suite Selection
    # ══════════════════════════════════════════════════════════
    elif step == 3:
        bld = get_building(st.session_state.os_building)
        if not bld:
            st.session_state.os_step = 0
            st.rerun()
            return

        bgt_max = st.session_state.os_budget_max
        min_sf = st.session_state.os_min_sf
        max_sf = st.session_state.os_max_sf

        matching = [s for s in bld["suites"] if s["status"] in AVAIL_STATUSES
                    and s.get("asking_rate") and s["asking_rate"] <= bgt_max
                    and min_sf <= (s.get("boma_rsf") or s.get("rsf", 0)) <= max_sf]

        st.markdown(
            '<div class="verdict-box" style="border-color:#16a34a;">'
            '<div class="verdict-label">Step 4 of 4 &mdash; Results</div>'
            '<div class="verdict-value" style="color:#16a34a;">{} Suite{} at {}</div>'
            '<div class="verdict-sub">Max ${}/sqft &mdash; {}</div>'
            '</div>'.format(
                len(matching), "s" if len(matching) != 1 else "",
                bld["name"], bgt_max, bld["address"]),
            unsafe_allow_html=True,
        )

        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("< Back to Buildings", key="back_to_bld"):
                st.session_state.os_step = 2
                st.rerun()
        with bc2:
            if st.button("Start Over", key="start_over"):
                st.session_state.os_step = 0
                st.session_state.os_building = None
                st.rerun()

        if not matching:
            st.markdown('<div class="alert-warn">No suites match. Try adjusting your criteria.</div>', unsafe_allow_html=True)
        else:
            rates = [s["asking_rate"] for s in matching]
            sizes = [(s.get("boma_rsf") or s.get("rsf", 0)) for s in matching]
            mkpi = []
            mkpi.append(kpi("Matches", str(len(matching)), "suites"))
            mkpi.append(kpi("Size Range", "{:,} - {:,}".format(min(sizes), max(sizes)), "sqft"))
            mkpi.append(kpi("Rate Range", "${:.0f} - ${:.0f}".format(min(rates), max(rates)), "per sqft/yr"))
            mkpi.append(kpi("Parking", bld.get("parking", "N/A"), "{} spaces".format((bld.get("parking_details") or {}).get("spaces", "N/A"))))
            st.markdown('<div class="kpi-grid">{}</div>'.format("".join(mkpi)), unsafe_allow_html=True)

            for s in matching:
                sf = s.get("boma_rsf") or s.get("rsf", 0)
                rate = s.get("asking_rate", 0)
                annual = rate * sf
                monthly = annual / 12
                suite_type = s.get("suite_type", "office").title()

                sc1, sc2 = st.columns([3, 2])
                with sc1:
                    st.markdown(
                        '<div class="card">'
                        '<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                        '<div>'
                        '<div style="font-size:1.15rem;font-weight:800;color:var(--navy);">Suite {suite}</div>'
                        '<div style="font-size:0.78rem;color:var(--slate-500);margin-top:0.15rem;">{bname}</div>'
                        '</div>'
                        '<div style="text-align:right;">'
                        '<div style="font-size:1.4rem;font-weight:800;color:#2563eb;">${rate:.2f}</div>'
                        '<div style="font-size:0.6rem;color:var(--slate-400);">per sqft/yr</div>'
                        '</div></div>'
                        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-top:1rem;text-align:center;">'
                        '<div><div style="font-size:0.55rem;color:var(--slate-500);text-transform:uppercase;">RSF</div><div style="font-size:1.05rem;font-weight:700;color:var(--navy);">{sf:,}</div></div>'
                        '<div><div style="font-size:0.55rem;color:var(--slate-500);text-transform:uppercase;">Annual</div><div style="font-size:1.05rem;font-weight:700;color:var(--navy);">{ann}</div></div>'
                        '<div><div style="font-size:0.55rem;color:var(--slate-500);text-transform:uppercase;">Monthly</div><div style="font-size:1.05rem;font-weight:700;color:var(--navy);">{mon}</div></div>'
                        '<div><div style="font-size:0.55rem;color:var(--slate-500);text-transform:uppercase;">Type</div><div style="font-size:1.05rem;font-weight:700;color:var(--navy);">{typ}</div></div>'
                        '</div></div>'.format(
                            suite=s["suite"], bname=bld["name"],
                            rate=rate, sf=sf,
                            ann=format_currency(annual), mon=format_currency(monthly),
                            typ=suite_type),
                        unsafe_allow_html=True,
                    )
                with sc2:
                    st.markdown(
                        '<div class="card" style="text-align:center;">'
                        '<div style="font-size:0.65rem;color:var(--slate-500);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">Floor Plan</div>'
                        '{}'
                        '</div>'.format(_floor_plan_svg(s["suite"], sf, suite_type)),
                        unsafe_allow_html=True,
                    )

            # Building features summary
            st.markdown('<div class="card"><div class="card-title">{} &mdash; Building Features</div>'.format(bld["name"]), unsafe_allow_html=True)

            fc1, fc2 = st.columns(2)
            with fc1:
                rows = ""
                rows += tr("Address", bld["address"])
                rows += tr("Class", bld["building_class"])
                rows += tr("Floors", str(bld["floors"]))
                rows += tr("Year Built", str(bld["year_built"]))
                rows += tr("Total RSF", "{:,}".format(bld["building_rsf"]))
                rows += tr("Occupancy", "{}%".format(bld["occupancy"]))
                st.markdown('<table class="dtable">{}</table>'.format(rows), unsafe_allow_html=True)
                st.markdown(_parking_card(bld), unsafe_allow_html=True)
                st.markdown(_rooftop_card(bld), unsafe_allow_html=True)
            with fc2:
                st.markdown('<div style="margin-bottom:0.5rem;font-size:0.72rem;font-weight:600;color:var(--navy);">Amenities</div>', unsafe_allow_html=True)
                st.markdown(_amenities_badges(bld["amenities"]), unsafe_allow_html=True)

                fig = go.Figure(data=[go.Pie(
                    labels=["Occupied", "Vacant"], values=[bld["occupied_rsf"], bld["vacant_rsf"]],
                    hole=0.6, marker=dict(colors=["#2563eb", "#e2e8f0"]),
                    textinfo="percent", hovertemplate="%{label}: %{value:,} sqft<extra></extra>")])
                fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                    font=dict(family="Inter", size=12),
                    annotations=[dict(text="{}%".format(bld["occupancy"]),
                        x=0.5, y=0.5, font_size=20, font_color="#0f172a", showarrow=False)])
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Comparison table
            st.markdown('<div class="card"><div class="card-title">Suite Comparison</div>', unsafe_allow_html=True)
            comp_data = []
            for s in matching:
                sf = s.get("boma_rsf") or s.get("rsf", 0)
                rate = s.get("asking_rate", 0)
                comp_data.append({
                    "Suite": s["suite"],
                    "RSF": "{:,}".format(sf),
                    "Rate ($/sqft/yr)": "${:.2f}".format(rate),
                    "Annual": format_currency(rate * sf),
                    "Monthly": format_currency(rate * sf / 12),
                })
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            with st.expander("Full Tenant Roll"):
                roll = []
                for s in bld["suites"]:
                    sf = s.get("boma_rsf") or s.get("rsf", 0)
                    roll.append({
                        "Suite": s["suite"],
                        "Tenant": s.get("tenant") or "VACANT",
                        "Status": s["status"].upper(),
                        "RSF": "{:,}".format(sf),
                        "Rate": "${:.2f}".format(s["rate"]) if s.get("rate") else "-",
                        "Lease End": s.get("lease_end") or "-",
                    })
                st.dataframe(pd.DataFrame(roll), use_container_width=True, hide_index=True)

            st.markdown('<div class="card"><div class="card-title">Location</div>', unsafe_allow_html=True)
            mp = folium.Map(location=[bld["lat"], bld["lon"]], zoom_start=15, tiles="CartoDB positron")
            folium.Marker([bld["lat"], bld["lon"]],
                popup=folium.Popup("<b>{}</b><br>{}".format(bld["name"], bld["address"]), max_width=250),
                icon=folium.Icon(color="blue", icon="building", prefix="fa")).add_to(mp)
            folium.Circle([bld["lat"], bld["lon"]], radius=500, color="#2563eb",
                fill=True, fill_opacity=0.05, weight=1.5).add_to(mp)
            st_folium(mp, width=None, height=350, returned_objects=[])
            st.markdown('</div>', unsafe_allow_html=True)
