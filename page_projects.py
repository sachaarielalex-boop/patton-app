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
    {
        "name": "Miami Green",
        "location": "3150 SW 38th Ave, Miami, FL 33146",
        "type": "Office",
        "status": "Active",
        "description": "Class B+ office tower in the Coral Gables / Coconut Grove corridor with Metrorail access.",
        "website": "miamigreenoffice.com",
    },
    {
        "name": "Coral Way Gardens",
        "location": "Coral Way, Miami, FL",
        "type": "Mixed-Use Development",
        "status": "In Development",
        "description": "Mixed-use development project along the vibrant Coral Way corridor.",
    },
    {
        "name": "Melrose Place",
        "location": "Miami, FL",
        "type": "Residential Development",
        "status": "In Development",
        "description": "Boutique residential project with comprehensive branding and modern design.",
    },
    {
        "name": "Emerald Place",
        "location": "Miami, FL",
        "type": "Residential Development",
        "status": "In Development",
        "description": "Branded residential development project in the Miami market.",
    },
    {
        "name": "Keystone Bay",
        "location": "Miami, FL",
        "type": "Waterfront Development",
        "status": "In Development",
        "description": "Waterfront-oriented development with premium bay views.",
    },
    {
        "name": "Keystone Towers",
        "location": "Miami, FL",
        "type": "High-Rise Development",
        "status": "In Development",
        "description": "High-rise tower development with dedicated project branding.",
    },
]

STATUS_COLORS = {
    "Active": ("var(--green-soft)", "var(--green-border)", "#16a34a"),
    "In Development": ("var(--accent-soft)", "var(--accent-border)", "var(--accent)"),
    "Pre-Development": ("var(--amber-soft)", "var(--amber-border)", "#d97706"),
}


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
