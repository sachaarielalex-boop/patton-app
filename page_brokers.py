"""Broker Database page – CRE broker contacts and office lease contacts."""
import streamlit as st


def _load_brokers():
    """Load broker data from embedded Python data."""
    from brokers_embedded import FIRMS, BROKERS, CONTACTS
    return FIRMS, BROKERS, CONTACTS


def render_brokers_page():
    import pandas as pd
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="brk_back"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Broker Database</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">South Florida CRE Contacts &mdash; Brokers, Firms & Lease Prospects</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    with st.spinner("Loading contacts..."):
        try:
            firms, brokers, contacts = _load_brokers()
        except Exception as e:
            st.error("Error loading broker data: {}".format(e))
            firms, brokers, contacts = [], [], []

    # KPIs
    st.markdown(
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem;">'
        '<div class="kpi-card"><div class="kl">CRE Firms</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Brokers</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Lease Contacts</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Total Contacts</div><div class="kv">{}</div></div>'
        '</div>'.format(len(firms), len(brokers), len(contacts), len(firms) + len(brokers) + len(contacts)),
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["Brokers ({})".format(len(brokers)), "CRE Firms ({})".format(len(firms)), "Lease Contacts ({})".format(len(contacts))])

    # ── Tab 1: Brokers ──
    with tab1:
        if brokers:
            import shared_db
            meta = shared_db.get("broker_meta", {})
            if not isinstance(meta, dict):
                meta = {}

            def _sector(b):
                m = meta.get(b["name"], {})
                if m.get("sector"):
                    return m["sector"]
                blob = (b.get("type", "") + " " + b.get("organization", "")).lower()
                if "residential" in blob:
                    return "Residential"
                return "Commercial"

            def _specialty(b):
                return meta.get(b["name"], {}).get("specialty", "")

            # Commercial / Residential separation at the top.
            sector_filter = st.radio(
                "Sector", ["All", "Commercial", "Residential"], horizontal=True, key="brk_sector")

            search = st.text_input("Search brokers", placeholder="Name, organization, specialty...", key="brk_search")

            filtered = brokers
            if sector_filter != "All":
                filtered = [b for b in filtered if _sector(b) == sector_filter]
            if search:
                q = search.lower()
                filtered = [b for b in filtered
                            if q in b["name"].lower() or q in b["organization"].lower()
                            or q in b["type"].lower() or q in _specialty(b).lower()]

            orgs = sorted(set(b["organization"] for b in filtered if b["organization"] and b["organization"] != "None"))
            org_filter = st.selectbox("Filter by organization", ["All"] + orgs, key="brk_org")
            if org_filter != "All":
                filtered = [b for b in filtered if b["organization"] == org_filter]

            st.markdown('<div style="font-size:0.72rem;color:var(--text-muted);margin-bottom:0.5rem;">{} brokers &mdash; edit Sector & Specialty inline, then Save.</div>'.format(len(filtered)), unsafe_allow_html=True)

            rows = []
            for b in filtered:
                linkedin = ""
                if b["linkedin"] and b["linkedin"] not in ("/", "/ ", "None", ""):
                    lnk = b["linkedin"].strip()
                    if not lnk.startswith("http"):
                        lnk = "https://" + lnk
                    linkedin = lnk
                rows.append({
                    "Name": b["name"],
                    "Sector": _sector(b),
                    "Specialty": _specialty(b),
                    "Organization": b["organization"],
                    "Email": b["email"],
                    "Mobile": b["mobile"],
                    "Market": b["market"],
                    "LinkedIn": linkedin,
                })
            df = pd.DataFrame(rows).astype(str)
            edited = st.data_editor(
                df, use_container_width=True, hide_index=True, key="brk_editor",
                column_config={
                    "Sector": st.column_config.SelectboxColumn(
                        "Sector", options=["Commercial", "Residential", "Both"], required=True),
                    "Specialty": st.column_config.TextColumn(
                        "Specialty", help="e.g. Office sales Brickell, Residential Coconut Grove"),
                    "Name": st.column_config.TextColumn("Name", disabled=True),
                    "Organization": st.column_config.TextColumn("Organization", disabled=True),
                    "Email": st.column_config.TextColumn("Email", disabled=True),
                    "Mobile": st.column_config.TextColumn("Mobile", disabled=True),
                    "Market": st.column_config.TextColumn("Market", disabled=True),
                    "LinkedIn": st.column_config.TextColumn("LinkedIn", disabled=True),
                },
            )
            if st.button("Save Sector & Specialty changes", key="brk_save", type="primary"):
                for _, r in edited.iterrows():
                    meta[r["Name"]] = {"sector": r["Sector"], "specialty": r["Specialty"]}
                shared_db.put("broker_meta", meta)
                st.success("Saved.")
                st.rerun()
        else:
            st.info("No broker data found.")

    # ── Tab 2: CRE Firms ──
    with tab2:
        if firms:
            rows = []
            for f in firms:
                rows.append({
                    "Firm": f["firm"],
                    "Category": f["category"],
                    "Website": f["website"],
                    "Status": f["status"],
                })
            df = pd.DataFrame(rows)
            st.dataframe(df.astype(str), use_container_width=True, hide_index=True)
        else:
            st.info("No firm data found.")

    # ── Tab 3: Lease Contacts ──
    with tab3:
        if contacts:
            search2 = st.text_input("Search contacts", placeholder="Name, type, market...", key="ct_search")
            filtered2 = contacts
            if search2:
                q = search2.lower()
                filtered2 = [c for c in contacts if q in c["name"].lower() or q in c.get("type", "").lower() or q in c.get("market", "").lower() or q in c.get("organization", "").lower()]

            # Market filter
            markets = sorted(set(c.get("market", "") for c in filtered2 if c.get("market") and c["market"] != "None"))
            mkt_filter = st.selectbox("Filter by market/area", ["All"] + markets, key="ct_mkt")
            if mkt_filter != "All":
                filtered2 = [c for c in filtered2 if c.get("market") == mkt_filter]

            st.markdown('<div style="font-size:0.72rem;color:var(--text-muted);margin-bottom:0.5rem;">{} contacts</div>'.format(len(filtered2)), unsafe_allow_html=True)

            rows = []
            for c in filtered2:
                rows.append({
                    "Name": c["name"],
                    "Organization": c.get("organization", ""),
                    "Type": c.get("type", ""),
                    "Email": c.get("email", ""),
                    "Mobile": c.get("mobile", ""),
                    "Market": c.get("market", ""),
                    "Address": c.get("address", ""),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df.astype(str), use_container_width=True, hide_index=True)
        else:
            st.info("No contact data found.")
