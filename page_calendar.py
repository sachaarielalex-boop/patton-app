"""Tenant Calendar – schedule visits, track tours, generate follow-up emails."""
import streamlit as st
import datetime
import shared_db


def _get_visits():
    return shared_db.get("tenant_visits", [])


def _save_visits(visits):
    shared_db.put("tenant_visits", visits)


def render_calendar_page():
    from utils.style import inject_css, LOGO_B64
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

    tab1, tab2, tab3 = st.tabs(["Schedule Visit", "Upcoming", "Follow-Up Email"])

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
                "Miami Green", "Doral Office Plaza", "Waterford Centre", "Other"
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
