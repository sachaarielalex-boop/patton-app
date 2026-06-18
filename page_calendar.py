"""Tenant Calendar – schedule visits, track tours, generate follow-up emails."""
import streamlit as st
import datetime
import calendar as _calmod
import shared_db

WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def _get_visits():
    return shared_db.get("tenant_visits", [])


def _save_visits(visits):
    shared_db.put("tenant_visits", visits)


def _get_contracts():
    c = shared_db.get("tenant_contracts", [])
    return c if isinstance(c, list) else []


def _save_contracts(contracts):
    shared_db.put("tenant_contracts", contracts)


def _years_between(d1, d2):
    """Whole + fractional years from d1 to d2 (can be negative)."""
    return (d2 - d1).days / 365.25


def _month_calendar_html(visits, today, year, month, lease_events=None):
    """Render a month grid with visit markers + lease start/end events."""
    by_day = {}
    for v in visits:
        try:
            d = datetime.date.fromisoformat(v["date"])
        except (ValueError, KeyError):
            continue
        if d.year == year and d.month == month:
            by_day.setdefault(d.day, []).append(v)

    lease_by_day = {}
    for ev in (lease_events or []):
        d = ev.get("date")
        if d and d.year == year and d.month == month:
            lease_by_day.setdefault(d.day, []).append(ev)

    head = "".join(
        '<div style="text-align:center;font-size:0.62rem;font-weight:700;letter-spacing:0.5px;'
        'text-transform:uppercase;color:var(--text-muted);padding:0.3rem 0;">{}</div>'.format(d)
        for d in WEEKDAYS
    )

    cells = ""
    weeks = _calmod.Calendar(firstweekday=6).monthdayscalendar(year, month)
    for week in weeks:
        for day in week:
            if day == 0:
                cells += ('<div style="min-height:74px;border-radius:8px;'
                          'background:transparent;"></div>')
                continue
            is_today = (year == today.year and month == today.month and day == today.day)
            dv = by_day.get(day, [])
            chips = ""
            for v in dv[:2]:
                if v.get("status") == "Completed":
                    c = "var(--green)"
                elif datetime.date(year, month, day) < today:
                    c = "var(--amber)"
                else:
                    c = "var(--accent)"
                chips += (
                    '<div style="display:flex;align-items:center;gap:3px;font-size:0.6rem;'
                    'color:var(--text-secondary);line-height:1.3;white-space:nowrap;overflow:hidden;'
                    'text-overflow:ellipsis;">'
                    '<span style="flex:0 0 5px;width:5px;height:5px;border-radius:50%;background:{c};"></span>'
                    '<span style="overflow:hidden;text-overflow:ellipsis;">{t} {tm}</span></div>'
                ).format(c=c, t=v.get("tenant", "")[:9], tm=v.get("time", ""))
            if len(dv) > 2:
                chips += ('<div style="font-size:0.58rem;color:var(--text-muted);">+{} more</div>'
                          .format(len(dv) - 2))
            lv = lease_by_day.get(day, [])
            for ev in lv[:2]:
                ec = "var(--green)" if ev.get("kind") == "start" else "var(--red)"
                tag = "start" if ev.get("kind") == "start" else "end"
                chips += (
                    '<div style="display:flex;align-items:center;gap:3px;font-size:0.58rem;'
                    'color:var(--text-tertiary);line-height:1.3;white-space:nowrap;overflow:hidden;'
                    'text-overflow:ellipsis;">'
                    '<span style="flex:0 0 5px;width:5px;height:5px;border-radius:2px;background:{c};"></span>'
                    '<span style="overflow:hidden;text-overflow:ellipsis;">{t} ({k})</span></div>'
                ).format(c=ec, t=ev.get("tenant", "")[:8], k=tag)
            if len(lv) > 2:
                chips += ('<div style="font-size:0.58rem;color:var(--text-muted);">+{} lease</div>'
                          .format(len(lv) - 2))
            daynum_col = "#fff" if is_today else "var(--text-secondary)"
            daynum_bg = "background:var(--accent);" if is_today else ""
            cell_border = "border:1px solid var(--accent);" if (dv or lv) else "border:1px solid var(--border);"
            cells += (
                '<div style="min-height:74px;border-radius:8px;{cb}background:var(--bg-card);'
                'padding:0.3rem;overflow:hidden;">'
                '<div style="display:inline-flex;align-items:center;justify-content:center;'
                'min-width:19px;height:19px;border-radius:50%;{db}font-size:0.66rem;font-weight:700;'
                'color:{dc};margin-bottom:0.15rem;">{day}</div>'
                '{chips}</div>'
            ).format(cb=cell_border, db=daynum_bg, dc=daynum_col, day=day, chips=chips)

    return (
        '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:0.2rem;">{head}</div>'
        '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;">{cells}</div>'
    ).format(head=head, cells=cells)


def render_calendar_page():
    from utils.style import inject_css, LOGO_B64, require_directory_access
    inject_css()

    if st.sidebar.button("Back to Home", key="cal_back"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Tenant Calendar</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Schedule visits, track tours &amp; generate follow-up emails</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    # Whole page (visits + lease contracts) is gated behind the patton.com code.
    if not require_directory_access("Tenant Calendar", key="cal_gate"):
        return

    visits = _get_visits()

    # KPIs
    today = datetime.date.today()
    upcoming = [v for v in visits if datetime.date.fromisoformat(v["date"]) >= today and v["status"] == "Scheduled"]
    completed = [v for v in visits if v["status"] == "Completed"]
    st.markdown(
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem;">'
        '<div class="kpi-card"><div class="kl">Total Visits</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Upcoming</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Completed</div><div class="kv">{}</div></div>'
        '</div>'.format(len(visits), len(upcoming), len(completed)),
        unsafe_allow_html=True,
    )

    tab1, tab2, tab4, tab3 = st.tabs(["Schedule Visit", "Upcoming", "Lease Contracts", "Follow-Up Email"])

    with tab4:
        _render_contracts(today)

    # ── Tab 1: Schedule ──
    with tab1:
        st.markdown("##### Schedule a New Visit")
        sc1, sc2 = st.columns(2)
        with sc1:
            tenant_name = st.text_input("Tenant / Prospect Name", key="cal_tenant")
            contact_email = st.text_input("Contact Email", key="cal_email")
            contact_phone = st.text_input("Contact Phone", key="cal_phone")
            company = st.text_input("Company", key="cal_company")
        with sc2:
            visit_date = st.date_input("Visit Date", value=today + datetime.timedelta(days=1), key="cal_date")
            visit_time = st.time_input("Visit Time", value=datetime.time(10, 0), key="cal_time")
            building = st.selectbox("Building", [
                "Miami Green", "Doral Office Plaza", "Waterford Centre", "4000 Ponce de Leon", "Other"
            ], key="cal_building")
            suites = st.text_input("Suites to Visit", placeholder="e.g. 200, 305, 410", key="cal_suites")

        notes = st.text_area("Notes", placeholder="Special requirements, parking instructions...", height=80, key="cal_notes")

        if st.button("Schedule Visit", type="primary", use_container_width=True, key="cal_schedule"):
            if not tenant_name:
                st.error("Enter a tenant name.")
            else:
                visit = {
                    "tenant": tenant_name.strip(),
                    "email": contact_email.strip(),
                    "phone": contact_phone.strip(),
                    "company": company.strip(),
                    "date": visit_date.isoformat(),
                    "time": visit_time.strftime("%H:%M"),
                    "building": building,
                    "suites": suites.strip(),
                    "notes": notes.strip(),
                    "status": "Scheduled",
                    "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "feedback": "",
                }
                visits.append(visit)
                _save_visits(visits)
                st.success("Visit scheduled: {} at {} on {}".format(tenant_name, building, visit_date))

                # Auto-create tenant folder
                folders = shared_db.get("tenant_folders", {})
                if tenant_name.strip() not in folders:
                    if st.button("Create Tenant Folder for {}".format(tenant_name), key="cal_create_folder"):
                        folders[tenant_name.strip()] = []
                        shared_db.put("tenant_folders", folders)
                        st.success("Folder created!")

    # ── Tab 2: Upcoming ──
    with tab2:
        # Month calendar with navigation.
        if "cal_view_year" not in st.session_state:
            st.session_state["cal_view_year"] = today.year
            st.session_state["cal_view_month"] = today.month
        vy = st.session_state["cal_view_year"]
        vm = st.session_state["cal_view_month"]

        nav_prev, nav_title, nav_next, nav_today = st.columns([1, 4, 1, 1])
        with nav_prev:
            if st.button("\u25c0", key="cal_prev_month", use_container_width=True):
                vm -= 1
                if vm < 1:
                    vm, vy = 12, vy - 1
                st.session_state["cal_view_month"], st.session_state["cal_view_year"] = vm, vy
                st.rerun()
        with nav_next:
            if st.button("\u25b6", key="cal_next_month", use_container_width=True):
                vm += 1
                if vm > 12:
                    vm, vy = 1, vy + 1
                st.session_state["cal_view_month"], st.session_state["cal_view_year"] = vm, vy
                st.rerun()
        with nav_today:
            if st.button("Today", key="cal_today_btn", use_container_width=True):
                st.session_state["cal_view_month"], st.session_state["cal_view_year"] = today.month, today.year
                st.rerun()
        with nav_title:
            st.markdown(
                '<div style="text-align:center;font-size:1.05rem;font-weight:800;'
                'color:var(--text-primary);padding-top:0.35rem;">{} {}</div>'.format(MONTHS[vm], vy),
                unsafe_allow_html=True,
            )

        lease_events = []
        for c in _collect_contracts():
            if c.get("start"):
                lease_events.append({"date": c["start"], "tenant": c["name"], "kind": "start"})
            if c.get("end"):
                lease_events.append({"date": c["end"], "tenant": c["name"], "kind": "end"})

        st.markdown(_month_calendar_html(visits, today, vy, vm, lease_events), unsafe_allow_html=True)
        st.markdown(
            '<div style="display:flex;gap:1rem;flex-wrap:wrap;font-size:0.66rem;color:var(--text-tertiary);margin:0.6rem 0 0.4rem;">'
            '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent);margin-right:4px;"></span>Scheduled</span>'
            '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--amber);margin-right:4px;"></span>Past due</span>'
            '<span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);margin-right:4px;"></span>Completed</span>'
            '<span><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:var(--green);margin-right:4px;"></span>Lease start</span>'
            '<span><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:var(--red);margin-right:4px;"></span>Lease end</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)

        if not visits:
            st.info("No visits scheduled yet.")
        else:
            sorted_visits = sorted(visits, key=lambda v: v["date"])
            for i, v in enumerate(sorted_visits):
                vdate = datetime.date.fromisoformat(v["date"])
                is_past = vdate < today
                status_badge = "badge-green" if v["status"] == "Completed" else ("badge-amber" if is_past else "badge-blue")

                st.markdown(
                    '<div class="card" style="padding:1rem 1.2rem;">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;">'
                    '<div>'
                    '<span style="font-size:0.95rem;font-weight:700;color:var(--text-primary);">{tenant}</span>'
                    ' <span class="badge {bc}">{status}</span>'
                    '</div>'
                    '<div style="font-size:0.82rem;font-weight:600;color:var(--accent);">{date} at {time}</div>'
                    '</div>'
                    '<div style="font-size:0.78rem;color:var(--text-tertiary);margin-top:0.3rem;">'
                    '{building}{suites}{company}'
                    '</div>'
                    '{notes}'
                    '</div>'.format(
                        tenant=v["tenant"], bc=status_badge, status=v["status"],
                        date=v["date"], time=v["time"], building=v["building"],
                        suites=" | Suites: {}".format(v["suites"]) if v["suites"] else "",
                        company=" | {}".format(v["company"]) if v["company"] else "",
                        notes='<div style="font-size:0.75rem;color:var(--text-muted);margin-top:0.3rem;font-style:italic;">{}</div>'.format(v["notes"]) if v["notes"] else "",
                    ),
                    unsafe_allow_html=True,
                )

                # Actions
                ac1, ac2, ac3 = st.columns(3)
                with ac1:
                    if v["status"] == "Scheduled" and st.button("Mark Completed", key="cal_done_{}".format(i)):
                        orig_idx = visits.index(v)
                        visits[orig_idx]["status"] = "Completed"
                        _save_visits(visits)
                        st.rerun()
                with ac2:
                    if v["status"] == "Completed" and not v.get("feedback"):
                        feedback = st.text_input("Tour feedback", key="cal_fb_{}".format(i), placeholder="Interested? Next steps?")
                        if feedback and st.button("Save", key="cal_fb_save_{}".format(i)):
                            orig_idx = visits.index(v)
                            visits[orig_idx]["feedback"] = feedback
                            _save_visits(visits)
                            st.rerun()
                with ac3:
                    if st.button("Delete", key="cal_del_{}".format(i)):
                        visits.remove(v)
                        _save_visits(visits)
                        st.rerun()

    # ── Tab 3: Follow-Up Email ──
    with tab3:
        st.markdown("##### Generate Follow-Up Email")
        completed_visits = [v for v in visits if v["status"] == "Completed"]
        if not completed_visits:
            st.info("Complete a visit first to generate a follow-up email.")
        else:
            visit_labels = ["{} - {} ({})".format(v["tenant"], v["building"], v["date"]) for v in completed_visits]
            sel_idx = st.selectbox("Select completed visit", range(len(visit_labels)), format_func=lambda x: visit_labels[x], key="cal_email_sel")
            sel_visit = completed_visits[sel_idx]

            tenant = sel_visit["tenant"]
            building = sel_visit["building"]
            suites_str = sel_visit["suites"]
            feedback = sel_visit.get("feedback", "")
            email_to = sel_visit.get("email", "")

            email_subject = "Follow-Up: {} Tour at {}".format(tenant, building)
            email_body = (
                "Dear {tenant},\n\n"
                "Thank you for taking the time to visit {building} on {date}. "
                "It was a pleasure showing you {suites_text}.\n\n"
                "{feedback_text}"
                "We believe {building} would be an excellent fit for your business needs. "
                "As discussed, I would like to present you with a formal lease proposal "
                "outlining the terms and conditions for the space.\n\n"
                "Please let me know if you have any questions or would like to schedule "
                "a follow-up meeting. I am available at your convenience.\n\n"
                "Best regards,\n"
                "Patton Real Estate Management\n"
                "Miami-Dade County, FL"
            ).format(
                tenant=tenant,
                building=building,
                date=sel_visit["date"],
                suites_text="Suite{}".format("s " + suites_str if suites_str else ""),
                feedback_text="Based on our tour, {}\n\n".format(feedback) if feedback else "",
            )

            st.markdown("**To:** {}".format(email_to or "(enter email above)"))
            st.markdown("**Subject:** {}".format(email_subject))
            st.text_area("Email Body", value=email_body, height=300, key="cal_email_body")

            ec1, ec2 = st.columns(2)
            with ec1:
                if st.button("Copy to Clipboard", key="cal_copy", use_container_width=True):
                    st.code(email_body, language=None)
                    st.info("Copy the text above.")
            with ec2:
                folders = shared_db.get("tenant_folders", {})
                if st.button("Save to Tenant Folder", key="cal_save_tf", use_container_width=True, type="primary"):
                    folder_name = tenant.strip()
                    if folder_name not in folders:
                        folders[folder_name] = []
                    folders[folder_name].append({
                        "type": "Follow-Up Email",
                        "tenant": tenant,
                        "filename": "email_followup_{}.txt".format(sel_visit["date"]),
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "fields": {"subject": email_subject, "body": email_body, "building": building},
                    })
                    shared_db.put("tenant_folders", folders)
                    st.success("Saved to folder: {}".format(folder_name))


def _parse_date(val):
    """Best-effort date parse for ISO or m/d/Y strings."""
    if not val:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%-m/%-d/%Y"):
        try:
            return datetime.datetime.strptime(str(val), fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def _collect_contracts():
    """Manual client contracts + portfolio leases that have an end date."""
    out = []
    for c in _get_contracts():
        out.append({
            "name": c.get("name", ""),
            "building": c.get("building", ""),
            "suite": c.get("suite", ""),
            "start": _parse_date(c.get("start")),
            "end": _parse_date(c.get("end")),
            "source": "client",
            "raw": c,
        })
    # Pull leased suites from the live portfolio.
    try:
        from utils.buildings_inventory import get_all_buildings
        for b in get_all_buildings():
            for s in b["suites"]:
                if s.get("tenant") and s.get("lease_end"):
                    out.append({
                        "name": s["tenant"],
                        "building": b["name"],
                        "suite": s.get("suite", ""),
                        "start": _parse_date(s.get("lease_start")),
                        "end": _parse_date(s.get("lease_end")),
                        "source": "portfolio",
                        "raw": None,
                    })
    except Exception:
        pass
    return out


def _render_contracts(today):
    st.markdown("##### Add a Client to the Calendar")
    cc1, cc2 = st.columns(2)
    with cc1:
        name = st.text_input("Client / Tenant Name", key="ct_name")
        building = st.selectbox("Building", [
            "Miami Green", "Doral Office Plaza", "Waterford Centre", "4000 Ponce de Leon", "Other"
        ], key="ct_building")
        suite = st.text_input("Suite", key="ct_suite", placeholder="e.g. 305")
    with cc2:
        start = st.date_input("Lease Start", value=today, key="ct_start")
        end = st.date_input(
            "Lease End", value=today.replace(year=today.year + 5), key="ct_end")

    if st.button("Add Client", type="primary", key="ct_add"):
        if not name.strip():
            st.error("Enter the client name.")
        elif end <= start:
            st.error("Lease End must be after Lease Start.")
        else:
            contracts = _get_contracts()
            contracts.append({
                "name": name.strip(), "building": building, "suite": suite.strip(),
                "start": start.isoformat(), "end": end.isoformat(),
            })
            _save_contracts(contracts)
            st.success("{} added until {}.".format(name.strip(), end.isoformat()))
            st.rerun()

    st.markdown("---")

    all_c = _collect_contracts()
    dated = [c for c in all_c if c["end"]]
    if not all_c:
        st.info("No client contracts yet. Add one above.")
        return

    # ── Tenure view: who's here, since when, for how long ──
    st.markdown("##### Tenure &mdash; who is here and for how long")
    for c in sorted(all_c, key=lambda x: (x["end"] or datetime.date.max)):
        parts = []
        if c["start"] and c["start"] <= today:
            yrs = _years_between(c["start"], today)
            parts.append("here for {:.1f} yr".format(yrs))
        elif c["start"]:
            parts.append("starts {}".format(c["start"].isoformat()))
        if c["end"]:
            left = _years_between(today, c["end"])
            if left >= 0:
                parts.append("{:.1f} yr left until end of contract".format(left))
            else:
                parts.append("expired {}".format(c["end"].isoformat()))
        loc = c["building"] + ((" Suite " + c["suite"]) if c["suite"] else "")
        tag = '<span class="badge badge-blue">client</span>' if c["source"] == "client" else '<span class="badge badge-green">portfolio</span>'
        with st.container(border=True):
            row1, row2 = st.columns([4, 1])
            with row1:
                st.markdown(
                    '<div style="font-size:0.95rem;font-weight:700;color:var(--text-primary);">{name} {tag}</div>'
                    '<div style="font-size:0.74rem;color:var(--text-tertiary);">{loc}</div>'
                    '<div style="font-size:0.74rem;color:var(--accent);font-weight:600;">{info}</div>'.format(
                        name=c["name"], tag=tag, loc=loc or "&mdash;",
                        info=" &middot; ".join(parts) or "no dates"),
                    unsafe_allow_html=True,
                )
            with row2:
                if c["source"] == "client" and st.button("Remove", key="ct_rm_{}_{}".format(c["name"][:10], c["suite"])):
                    contracts = _get_contracts()
                    contracts = [x for x in contracts if not (
                        x.get("name") == c["raw"].get("name") and x.get("suite") == c["raw"].get("suite")
                        and x.get("end") == c["raw"].get("end"))]
                    _save_contracts(contracts)
                    st.rerun()

    # ── Lease expirations by year (pie chart) ──
    if dated:
        st.markdown("---")
        st.markdown("##### Lease expirations by year")
        from collections import Counter
        import plotly.graph_objects as go

        counts = Counter(c["end"].year for c in dated)
        years = sorted(counts)
        labels = [str(y) for y in years]
        values = [counts[y] for y in years]
        # Highlight the soonest expirations with warmer colors.
        palette = ["#dc2626", "#ea580c", "#d97706", "#ca8a04", "#16a34a",
                   "#0d9488", "#2563eb", "#7c3aed", "#9333ea", "#64748b"]
        colors = [palette[i % len(palette)] for i in range(len(years))]

        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.5,
            marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
            textinfo="label+value", textfont=dict(size=13),
            hovertemplate="%{label}: %{value} lease(s) ending<extra></extra>",
            sort=False,
        )])
        fig.update_layout(
            height=320, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15),
            annotations=[dict(text="{}<br>leases".format(len(dated)), x=0.5, y=0.5,
                              font=dict(size=16, color="#94a3b8"), showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Each slice = number of leases ending that year. Click a member in the Tenure list above for details.")
