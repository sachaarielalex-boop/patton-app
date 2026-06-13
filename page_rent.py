"""Rent Tracker – upload rent rolls, track tenant payments."""
import streamlit as st
import datetime
import shared_db


def _get_rent_data():
    return shared_db.get("rent_tracker", {})


def _save_rent_data(data):
    shared_db.put("rent_tracker", data)


def render_rent_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="rent_back"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Rent Tracker</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Track tenant payments across your buildings</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    rent_data = _get_rent_data()

    tab1, tab2, tab3 = st.tabs(["Upload Rent Roll", "Payment Status", "Summary"])

    # ── Tab 1: Upload ──
    with tab1:
        st.markdown("##### Upload Rent Roll")
        st.markdown(
            '<div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:1rem;">'
            'Upload an Excel or CSV file with tenant payment data. Expected columns: '
            'Tenant, Suite, Monthly Rent, Jan, Feb, Mar, etc. (or any month columns with Paid/Unpaid).</div>',
            unsafe_allow_html=True,
        )

        building_name = st.text_input("Building Name", key="rent_building")
        uploaded = st.file_uploader("Upload Rent Roll", type=["xlsx", "csv"], key="rent_upload")

        if uploaded and building_name:
            try:
                import pandas as pd
                if uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded)

                st.success("Loaded {} rows from {}".format(len(df), uploaded.name))
                st.dataframe(df, use_container_width=True)

                if st.button("Save Rent Roll", type="primary", key="rent_save"):
                    # Convert to list of dicts for session state storage
                    records = df.astype(str).to_dict("records")
                    columns = list(df.columns)
                    rent_data[building_name] = {
                        "records": records,
                        "columns": columns,
                        "filename": uploaded.name,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    _save_rent_data(rent_data)
                    st.success("Rent roll saved for {}!".format(building_name))
                    st.rerun()

            except Exception as e:
                st.error("Error reading file: {}".format(str(e)))

        if not uploaded:
            st.markdown("---")
            st.markdown("##### Or Add Tenants Manually")

            if "manual_tenants" not in st.session_state:
                st.session_state["manual_tenants"] = []

            manual_building = st.text_input("Building", key="rent_manual_bldg")
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                m_tenant = st.text_input("Tenant Name", key="rent_m_tenant")
            with mc2:
                m_suite = st.text_input("Suite", key="rent_m_suite")
            with mc3:
                m_rent = st.text_input("Monthly Rent ($)", key="rent_m_rent")

            if st.button("Add Tenant", key="rent_add_manual"):
                if m_tenant and manual_building:
                    if manual_building not in rent_data:
                        rent_data[manual_building] = {
                            "records": [],
                            "columns": ["Tenant", "Suite", "Monthly Rent", "Status"],
                            "filename": "manual",
                            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                    rent_data[manual_building]["records"].append({
                        "Tenant": m_tenant,
                        "Suite": m_suite,
                        "Monthly Rent": m_rent,
                        "Status": "Pending",
                    })
                    _save_rent_data(rent_data)
                    st.success("Added {} to {}".format(m_tenant, manual_building))
                    st.rerun()

    # ── Tab 2: Payment Status ──
    with tab2:
        if not rent_data:
            st.info("No rent rolls uploaded yet. Go to the Upload tab to add data.")
        else:
            building_select = st.selectbox(
                "Select Building",
                list(rent_data.keys()),
                key="rent_view_bldg",
            )

            if building_select and building_select in rent_data:
                bdata = rent_data[building_select]
                records = bdata["records"]

                st.markdown(
                    '<div style="font-size:0.72rem;color:var(--text-muted);margin-bottom:0.5rem;">'
                    'File: {} | Uploaded: {} | {} tenants</div>'.format(
                        bdata["filename"], bdata["date"], len(records)
                    ),
                    unsafe_allow_html=True,
                )

                current_month = datetime.datetime.now().strftime("%B")

                for i, rec in enumerate(records):
                    tenant_name = rec.get("Tenant", rec.get("tenant", "Unknown"))
                    suite = rec.get("Suite", rec.get("suite", "N/A"))
                    rent_amt = rec.get("Monthly Rent", rec.get("monthly_rent", "N/A"))
                    status = rec.get("Status", rec.get(current_month, "Pending"))

                    is_paid = str(status).lower() in ("paid", "yes", "1", "true", "oui")
                    status_color = "#059669" if is_paid else "#dc2626"
                    status_bg = "rgba(5,150,105,0.08)" if is_paid else "rgba(220,38,38,0.08)"
                    status_text = "PAID" if is_paid else "UNPAID"

                    st.markdown(
                        '<div style="display:flex;align-items:center;justify-content:space-between;'
                        'padding:0.8rem 1rem;background:var(--bg-card);border:1px solid var(--border);'
                        'border-radius:var(--radius-sm);margin-bottom:0.4rem;">'
                        '<div>'
                        '<div style="font-size:0.88rem;font-weight:600;color:var(--text-primary);">{tenant}</div>'
                        '<div style="font-size:0.72rem;color:var(--text-muted);">Suite {suite} | ${rent}/mo</div>'
                        '</div>'
                        '<div style="display:flex;align-items:center;gap:0.8rem;">'
                        '<span style="font-size:0.65rem;font-weight:700;color:{sc};background:{sb};'
                        'padding:0.25rem 0.8rem;border-radius:20px;letter-spacing:0.5px;">{st}</span>'
                        '</div>'
                        '</div>'.format(
                            tenant=tenant_name, suite=suite, rent=rent_amt,
                            sc=status_color, sb=status_bg, st=status_text,
                        ),
                        unsafe_allow_html=True,
                    )

                    rc1, rc2 = st.columns([0.5, 0.5])
                    with rc1:
                        if not is_paid:
                            if st.button("Mark as Paid", key="rent_paid_{}".format(i)):
                                if "Status" in rec:
                                    rec["Status"] = "Paid"
                                elif current_month in rec:
                                    rec[current_month] = "Paid"
                                else:
                                    rec["Status"] = "Paid"
                                _save_rent_data(rent_data)
                                st.rerun()
                        else:
                            if st.button("Mark as Unpaid", key="rent_unpaid_{}".format(i)):
                                if "Status" in rec:
                                    rec["Status"] = "Unpaid"
                                elif current_month in rec:
                                    rec[current_month] = "Unpaid"
                                else:
                                    rec["Status"] = "Unpaid"
                                _save_rent_data(rent_data)
                                st.rerun()
                    with rc2:
                        if st.button("Remove", key="rent_del_{}".format(i)):
                            records.pop(i)
                            _save_rent_data(rent_data)
                            st.rerun()

    # ── Tab 3: Summary ──
    with tab3:
        if not rent_data:
            st.info("No data yet.")
        else:
            total_tenants = 0
            total_paid = 0
            total_unpaid = 0
            total_revenue = 0.0
            collected = 0.0

            current_month = datetime.datetime.now().strftime("%B")

            for bname, bdata in rent_data.items():
                for rec in bdata["records"]:
                    total_tenants += 1
                    status = rec.get("Status", rec.get(current_month, "Pending"))
                    is_paid = str(status).lower() in ("paid", "yes", "1", "true", "oui")

                    rent_str = rec.get("Monthly Rent", rec.get("monthly_rent", "0"))
                    try:
                        rent_val = float(str(rent_str).replace("$", "").replace(",", "").strip())
                    except (ValueError, TypeError):
                        rent_val = 0.0

                    total_revenue += rent_val
                    if is_paid:
                        total_paid += 1
                        collected += rent_val
                    else:
                        total_unpaid += 1

            pct = int(100 * total_paid / total_tenants) if total_tenants > 0 else 0
            pct_color = "#059669" if pct >= 80 else ("#d97706" if pct >= 50 else "#dc2626")

            kc1, kc2, kc3, kc4 = st.columns(4)
            with kc1:
                st.markdown(
                    '<div class="card" style="text-align:center;padding:1.2rem;">'
                    '<div style="font-size:1.6rem;font-weight:800;color:var(--text-primary);">{}</div>'
                    '<div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-top:0.3rem;">Total Tenants</div>'
                    '</div>'.format(total_tenants),
                    unsafe_allow_html=True,
                )
            with kc2:
                st.markdown(
                    '<div class="card" style="text-align:center;padding:1.2rem;">'
                    '<div style="font-size:1.6rem;font-weight:800;color:#059669;">{}</div>'
                    '<div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-top:0.3rem;">Paid</div>'
                    '</div>'.format(total_paid),
                    unsafe_allow_html=True,
                )
            with kc3:
                st.markdown(
                    '<div class="card" style="text-align:center;padding:1.2rem;">'
                    '<div style="font-size:1.6rem;font-weight:800;color:#dc2626;">{}</div>'
                    '<div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-top:0.3rem;">Unpaid</div>'
                    '</div>'.format(total_unpaid),
                    unsafe_allow_html=True,
                )
            with kc4:
                st.markdown(
                    '<div class="card" style="text-align:center;padding:1.2rem;">'
                    '<div style="font-size:1.6rem;font-weight:800;color:{pc};">{pct}%</div>'
                    '<div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-top:0.3rem;">Collection Rate</div>'
                    '</div>'.format(pc=pct_color, pct=pct),
                    unsafe_allow_html=True,
                )

            st.markdown('<div style="height:0.8rem;"></div>', unsafe_allow_html=True)

            # Revenue summary
            outstanding = total_revenue - collected
            st.markdown(
                '<div class="card" style="padding:1.2rem;">'
                '<div style="font-size:0.9rem;font-weight:700;color:var(--text-primary);margin-bottom:0.8rem;">Revenue Summary</div>'
                '<div style="display:flex;justify-content:space-between;padding:0.4rem 0;border-bottom:1px solid var(--border);">'
                '<span style="font-size:0.8rem;color:var(--text-tertiary);">Expected Monthly Revenue</span>'
                '<span style="font-size:0.85rem;font-weight:600;color:var(--text-primary);">${:,.2f}</span></div>'
                '<div style="display:flex;justify-content:space-between;padding:0.4rem 0;border-bottom:1px solid var(--border);">'
                '<span style="font-size:0.8rem;color:var(--text-tertiary);">Collected</span>'
                '<span style="font-size:0.85rem;font-weight:600;color:#059669;">${:,.2f}</span></div>'
                '<div style="display:flex;justify-content:space-between;padding:0.4rem 0;">'
                '<span style="font-size:0.8rem;color:var(--text-tertiary);">Outstanding</span>'
                '<span style="font-size:0.85rem;font-weight:600;color:#dc2626;">${:,.2f}</span></div>'
                '</div>'.format(total_revenue, collected, outstanding),
                unsafe_allow_html=True,
            )

            # Per-building breakdown
            if len(rent_data) > 1:
                st.markdown("---")
                st.markdown("##### By Building")
                for bname, bdata in rent_data.items():
                    b_total = len(bdata["records"])
                    b_paid = sum(
                        1 for r in bdata["records"]
                        if str(r.get("Status", r.get(current_month, ""))).lower() in ("paid", "yes", "1", "true", "oui")
                    )
                    b_pct = int(100 * b_paid / b_total) if b_total > 0 else 0
                    bar_color = "#059669" if b_pct >= 80 else ("#d97706" if b_pct >= 50 else "#dc2626")
                    st.markdown(
                        '<div style="margin-bottom:0.6rem;">'
                        '<div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">'
                        '<span style="font-size:0.8rem;font-weight:600;color:var(--text-primary);">{name}</span>'
                        '<span style="font-size:0.75rem;color:var(--text-muted);">{paid}/{total} paid ({pct}%)</span>'
                        '</div>'
                        '<div style="background:var(--bg-tertiary);border-radius:6px;height:8px;overflow:hidden;">'
                        '<div style="background:{color};height:100%;width:{pct}%;border-radius:6px;transition:width 0.3s;"></div>'
                        '</div></div>'.format(
                            name=bname, paid=b_paid, total=b_total, pct=b_pct, color=bar_color,
                        ),
                        unsafe_allow_html=True,
                    )
