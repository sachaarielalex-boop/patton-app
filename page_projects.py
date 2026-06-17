"""Upcoming Projects page – Patton development projects portfolio."""
import streamlit as st


PROJECTS = [
    {
        "name": "Allapattah House",
        "location": "Allapattah, Miami, FL",
        "type": "Residential Development",
        "status": "In Development",
        "description": "Modern residential development in Miami's fast-growing Allapattah neighborhood.",
    },
]

STATUS_COLORS = {
    "Active": ("var(--green-soft)", "var(--green-border)", "#16a34a"),
    "In Development": ("var(--accent-soft)", "var(--accent-border)", "var(--accent)"),
    "Pre-Development": ("var(--amber-soft)", "var(--amber-border)", "#d97706"),
}


def _fmt_money(v):
    try:
        v = float(v)
    except (ValueError, TypeError):
        return "$0"
    if abs(v) >= 1e6:
        return "${:.1f}M".format(v / 1e6)
    if abs(v) >= 1e3:
        return "${:.0f}K".format(v / 1e3)
    return "${:,.0f}".format(v)


def render_projects_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="proj_back"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Upcoming Projects</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Patton Commercial Real Estate &mdash; Development Portfolio</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    # ── Studio Projects (user-created) ─────────────────────
    import shared_db
    studio = shared_db.get("projects", [])

    sh1, sh2 = st.columns([3, 1])
    with sh1:
        st.markdown(
            '<div style="font-size:1rem;font-weight:800;color:var(--text-primary);margin:0.3rem 0;">'
            'My Studio Projects</div>'
            '<div style="font-size:0.74rem;color:var(--text-muted);margin-bottom:0.6rem;">'
            'Developments you designed in Project Studio</div>',
            unsafe_allow_html=True,
        )
    with sh2:
        if st.button("+ New Project", key="proj_new_studio", type="primary", use_container_width=True):
            st.session_state.pop("_proj", None)
            st.session_state["_proj_step"] = 0
            st.session_state["app_mode"] = "project_creator"
            st.rerun()

    if not studio:
        st.markdown(
            '<div class="card" style="text-align:center;padding:2rem;border:2px dashed var(--border);">'
            '<div style="font-size:2rem;margin-bottom:0.5rem;">&#127959;</div>'
            '<div style="font-size:0.9rem;font-weight:700;color:var(--text-primary);">No studio projects yet</div>'
            '<div style="font-size:0.78rem;color:var(--text-tertiary);margin-top:0.3rem;">'
            'Click "+ New Project" above, or use "Open Project Studio" from a Property Search.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for i in range(0, len(studio), 2):
            scols = st.columns(2, gap="large")
            for j, scol in enumerate(scols):
                sidx = i + j
                if sidx >= len(studio):
                    break
                sp = studio[sidx]
                summ = sp.get("summary", {})
                pcol = "var(--green)" if summ.get("profit", 0) > 0 else "var(--red)"
                with scol:
                    st.markdown(
                        '<div class="card" style="padding:1.3rem;">'
                        '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);">{name}</div>'
                        '<div style="font-size:0.74rem;color:var(--text-tertiary);margin:0.2rem 0 0.6rem;">{addr}</div>'
                        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">'
                        '<div><div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:1px;color:var(--text-muted);font-weight:700;">Units</div>'
                        '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);">{units}</div></div>'
                        '<div><div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:1px;color:var(--text-muted);font-weight:700;">Floors</div>'
                        '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);">{floors}</div></div>'
                        '<div><div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:1px;color:var(--text-muted);font-weight:700;">Profit</div>'
                        '<div style="font-size:1.05rem;font-weight:800;color:{pcol};">{profit}</div></div>'
                        '<div><div style="font-size:0.55rem;text-transform:uppercase;letter-spacing:1px;color:var(--text-muted);font-weight:700;">Margin</div>'
                        '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);">{margin}%</div></div>'
                        '</div>'
                        '<div style="font-size:0.62rem;color:var(--text-muted);margin-top:0.6rem;">Saved {saved}</div>'
                        '</div>'.format(
                            name=sp.get("name", "Untitled"), addr=sp.get("address") or "-",
                            units=summ.get("units", "-"), floors=summ.get("floors", "-"),
                            profit=_fmt_money(summ.get("profit", 0)), pcol=pcol,
                            margin=summ.get("margin", 0), saved=sp.get("saved", ""),
                        ),
                        unsafe_allow_html=True,
                    )
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("Edit", key="proj_edit_{}".format(sidx), use_container_width=True):
                            st.session_state["_proj"] = dict(sp.get("inputs", {}))
                            st.session_state["_proj_step"] = 0
                            st.session_state["app_mode"] = "project_creator"
                            st.rerun()
                    with ec2:
                        if st.button("Delete", key="proj_del_{}".format(sidx), use_container_width=True):
                            studio.pop(sidx)
                            shared_db.put("projects", studio)
                            st.rerun()

    st.markdown('<div style="height:1.5rem;"></div><hr style="border-color:var(--border);">', unsafe_allow_html=True)

    # KPI row
    active = sum(1 for p in PROJECTS if p["status"] == "Active")
    dev = sum(1 for p in PROJECTS if p["status"] == "In Development")
    st.markdown(
        '<div style="display:flex;gap:1rem;margin-bottom:1.5rem;">'
        '<div class="kpi-card"><div class="kl">Total Projects</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Active</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">In Development</div><div class="kv">{}</div></div>'
        '</div>'.format(len(PROJECTS), active, dev),
        unsafe_allow_html=True,
    )

    # Project cards
    for i in range(0, len(PROJECTS), 2):
        cols = st.columns(2, gap="large")
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(PROJECTS):
                break
            p = PROJECTS[idx]
            sc = STATUS_COLORS.get(p["status"], STATUS_COLORS["In Development"])
            website_link = ""
            if p.get("website"):
                website_link = '<a href="https://{}" target="_blank" style="font-size:0.72rem;color:var(--accent);text-decoration:none;">{} &rarr;</a>'.format(p["website"], p["website"])
            with col:
                st.markdown(
                    '<div class="card" style="padding:1.5rem;min-height:200px;">'
                    '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.8rem;">'
                    '<div style="font-size:1.1rem;font-weight:800;color:var(--text-primary);">{name}</div>'
                    '<span style="font-size:0.62rem;font-weight:700;padding:0.2rem 0.6rem;border-radius:20px;background:{sbg};border:1px solid {sbd};color:{sc};">{status}</span>'
                    '</div>'
                    '<div style="font-size:0.78rem;color:var(--text-tertiary);margin-bottom:0.3rem;">{loc}</div>'
                    '<div style="font-size:0.68rem;color:var(--text-muted);letter-spacing:1px;text-transform:uppercase;margin-bottom:0.8rem;">{ptype}</div>'
                    '<p style="font-size:0.8rem;color:var(--text-secondary);line-height:1.6;margin:0 0 0.5rem;">{desc}</p>'
                    '{website}'
                    '</div>'.format(
                        name=p["name"], loc=p["location"], ptype=p["type"],
                        status=p["status"], desc=p["description"],
                        sbg=sc[0], sbd=sc[1], sc=sc[2],
                        website=website_link,
                    ),
                    unsafe_allow_html=True,
                )

    st.markdown(
        '<div style="text-align:center;margin-top:2rem;padding:1rem;">'
        '<a href="https://www.pattonre.com/developmentprojects" target="_blank" '
        'style="font-size:0.8rem;color:var(--accent);text-decoration:none;font-weight:600;">'
        'View all projects on pattonre.com &rarr;</a>'
        '</div>',
        unsafe_allow_html=True,
    )
