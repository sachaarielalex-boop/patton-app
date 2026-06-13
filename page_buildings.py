"""Our Buildings page – view portfolio buildings, suites, and floor plans."""
import streamlit as st


def render_buildings_page():
    from utils.style import inject_css, LOGO_B64
    from utils.buildings_inventory import BUILDINGS
    inject_css()

    if st.sidebar.button("Back to Home", key="bldg_back"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Our Buildings</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Patton Commercial Real Estate &mdash; Portfolio Overview</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    # Portfolio KPIs
    total_rsf = sum(b["building_rsf"] for b in BUILDINGS)
    total_vacant = sum(b["vacant_rsf"] for b in BUILDINGS)
    total_suites = sum(len(b["suites"]) for b in BUILDINGS)
    avail_suites = sum(1 for b in BUILDINGS for s in b["suites"] if s["status"] in ("vacant", "expired"))
    avg_occ = sum(b["occupancy"] for b in BUILDINGS) / len(BUILDINGS) if BUILDINGS else 0

    st.markdown(
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem;">'
        '<div class="kpi-card"><div class="kl">Buildings</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Total RSF</div><div class="kv">{:,}</div></div>'
        '<div class="kpi-card"><div class="kl">Avg Occupancy</div><div class="kv">{:.0f}%</div></div>'
        '<div class="kpi-card"><div class="kl">Available Suites</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Vacant RSF</div><div class="kv">{:,}</div></div>'
        '</div>'.format(len(BUILDINGS), total_rsf, avg_occ, avail_suites, total_vacant),
        unsafe_allow_html=True,
    )

    # Building selector
    bldg_names = [b["name"] for b in BUILDINGS]
    tabs = st.tabs(bldg_names)

    for tab, bldg in zip(tabs, BUILDINGS):
        with tab:
            _render_building(bldg)


def _render_building(bldg):
    import pandas as pd
    from utils.style import tr
    from utils.property_data import format_currency, format_number

    # Building info card
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="card"><div class="card-title">Building Details</div>', unsafe_allow_html=True)
        rows = ""
        rows += tr("Address", bldg["address"])
        rows += tr("Submarket", bldg["submarket"])
        rows += tr("Class", bldg["building_class"])
        rows += tr("Floors", str(bldg["floors"]))
        rows += tr("Year Built", str(bldg["year_built"]))
        rows += tr("Total RSF", "{:,} sqft".format(bldg["building_rsf"]))
        rows += tr("Occupied RSF", "{:,} sqft".format(bldg["occupied_rsf"]))
        rows += tr("Vacant RSF", "{:,} sqft".format(bldg["vacant_rsf"]))
        rows += tr("Occupancy", "{}%".format(bldg["occupancy"]))
        rows += tr("Parking", bldg["parking"])
        if bldg.get("parking_details"):
            pd_info = bldg["parking_details"]
            rows += tr("Parking Spaces", str(pd_info.get("spaces", "N/A")))
            rows += tr("Parking Ratio", pd_info.get("ratio", "N/A"))
        st.markdown('<table class="dtable">{}</table></div>'.format(rows), unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card"><div class="card-title">Amenities</div>', unsafe_allow_html=True)
        for a in bldg.get("amenities", []):
            st.markdown(
                '<div style="padding:0.35rem 0;border-bottom:1px solid var(--border);font-size:0.82rem;color:var(--text-secondary);">'
                '&#x2713; {}</div>'.format(a),
                unsafe_allow_html=True,
            )
        if bldg.get("rooftop") and bldg["rooftop"].get("access"):
            st.markdown(
                '<div style="margin-top:0.8rem;padding:0.6rem;background:var(--accent-soft);border:1px solid var(--accent-border);border-radius:8px;">'
                '<div style="font-size:0.75rem;font-weight:700;color:var(--accent);margin-bottom:0.3rem;">Rooftop Access</div>'
                '{}</div>'.format(
                    "".join('<div style="font-size:0.72rem;color:var(--text-tertiary);">&#x2022; {}</div>'.format(f) for f in bldg["rooftop"].get("features", []))
                ),
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Suite table
    st.markdown('<div class="card"><div class="card-title">Suite Directory</div>', unsafe_allow_html=True)

    suite_rows = []
    for s in bldg["suites"]:
        status = s["status"].title()
        status_color = "#16a34a" if status == "Occupied" else ("#dc2626" if status == "Vacant" else "#d97706")
        rate_str = "${:.2f}/sqft".format(s["rate"]) if s.get("rate") else "-"
        asking = "${:.2f}/sqft".format(s["asking_rate"]) if s.get("asking_rate") else "-"
        suite_rows.append({
            "Suite": s["suite"],
            "RSF": "{:,}".format(s["rsf"]),
            "Tenant": s.get("tenant") or "-",
            "Status": status,
            "Rate": rate_str,
            "Asking": asking,
            "Lease End": s.get("lease_end") or "-",
            "Annual Inc.": "{}%".format(s.get("annual_inc")) if s.get("annual_inc") else "-",
        })

    df = pd.DataFrame(suite_rows)
    st.dataframe(df.astype(str), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Available suites highlight
    avail = [s for s in bldg["suites"] if s["status"] in ("vacant", "expired")]
    if avail:
        st.markdown('<div class="card"><div class="card-title">Available Suites ({} units)</div>'.format(len(avail)), unsafe_allow_html=True)
        for s in avail:
            status_label = "VACANT" if s["status"] == "vacant" else "EXPIRED"
            badge_class = "badge-red" if s["status"] == "vacant" else "badge-amber"
            asking = "${:.2f}/sqft".format(s["asking_rate"]) if s.get("asking_rate") else "Call for pricing"
            tenant_info = ""
            if s.get("tenant"):
                tenant_info = '<div style="font-size:0.72rem;color:var(--text-muted);">Previous tenant: {}</div>'.format(s["tenant"])

            # Floor plan SVG
            sqft = s["rsf"]
            svg_w = min(max(sqft / 30, 100), 400)
            svg_h = svg_w * 0.6

            st.markdown(
                '<div style="border:1px solid var(--border);border-radius:10px;padding:1.2rem;margin-bottom:0.8rem;background:var(--bg-secondary);">'
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">'
                '<div>'
                '<span style="font-size:1rem;font-weight:800;color:var(--text-primary);">Suite {suite}</span>'
                ' <span class="badge {bc}">{sl}</span>'
                '</div>'
                '<div style="font-size:0.9rem;font-weight:700;color:var(--accent);">{asking}</div>'
                '</div>'
                '<div style="font-size:0.82rem;color:var(--text-secondary);margin-bottom:0.3rem;">{rsf:,} RSF</div>'
                '{tenant}'
                '<div style="margin-top:0.8rem;">'
                '<svg viewBox="0 0 {w} {h}" style="max-width:350px;border:1px solid var(--border);border-radius:6px;background:#f8fafc;">'
                '<rect x="2" y="2" width="{rw}" height="{rh}" rx="4" fill="none" stroke="#2563eb" stroke-width="1.5"/>'
                '<text x="{tx}" y="{ty}" text-anchor="middle" fill="#2563eb" font-size="11" font-weight="600">Suite {suite}</text>'
                '<text x="{tx}" y="{ty2}" text-anchor="middle" fill="#64748b" font-size="9">{rsf:,} sqft</text>'
                '<rect x="2" y="{dh}" width="20" height="{dd}" fill="#2563eb" rx="1"/>'
                '</svg>'
                '</div>'
                '</div>'.format(
                    suite=s["suite"], bc=badge_class, sl=status_label,
                    asking=asking, rsf=sqft, tenant=tenant_info,
                    w=int(svg_w), h=int(svg_h), rw=int(svg_w - 4), rh=int(svg_h - 4),
                    tx=int(svg_w / 2), ty=int(svg_h / 2 - 5), ty2=int(svg_h / 2 + 10),
                    dh=int(svg_h * 0.4), dd=int(svg_h * 0.2),
                ),
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:0.65rem;color:var(--text-muted);text-align:center;margin-top:1rem;">'
        '{}</div>'.format(bldg.get("description", "")),
        unsafe_allow_html=True,
    )
