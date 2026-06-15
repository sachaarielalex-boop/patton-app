"""Tenant Folder page – organize lease documents by tenant."""
import streamlit as st
import base64
import datetime
import shared_db

_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def render_tenants_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="ten_back"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Tenant Folders</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Lease abstracts, proposals & documents organized by tenant</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    folders = shared_db.get("tenant_folders", {})
    scan_history = shared_db.get("scan_history", [])

    # KPIs
    total_docs = sum(len(docs) for docs in folders.values())
    st.markdown(
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem;">'
        '<div class="kpi-card"><div class="kl">Tenant Folders</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Documents</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Past Scans</div><div class="kv">{}</div></div>'
        '</div>'.format(len(folders), total_docs, len(scan_history)),
        unsafe_allow_html=True,
    )

    # Create new folder
    st.markdown("##### Create New Tenant Folder")
    nc1, nc2 = st.columns([3, 1])
    with nc1:
        new_name = st.text_input("Tenant name", placeholder="e.g. Kety Ferrier", key="ten_new_name")
    with nc2:
        st.markdown('<div style="height:1.7rem;"></div>', unsafe_allow_html=True)
        if st.button("Create Folder", key="ten_create", type="primary"):
            if new_name.strip():
                if new_name.strip() not in folders:
                    folders[new_name.strip()] = []
                    shared_db.put("tenant_folders", folders)
                    st.success("Created folder: {}".format(new_name.strip()))
                    st.rerun()
                else:
                    st.warning("Folder already exists.")

    st.markdown("---")

    # Quick link to Lease Abstract
    st.markdown("##### Quick Actions")
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("Go to Lease Abstract", key="ten_go_abstract", use_container_width=True, type="primary"):
            st.session_state["app_mode"] = "abstract"
            st.rerun()
    with qa2:
        if st.button("Go to Lease Proposal", key="ten_go_proposal", use_container_width=True):
            st.session_state["app_mode"] = "proposal"
            st.rerun()

    st.markdown("---")

    if not folders and not scan_history:
        st.markdown(
            '<div class="card" style="text-align:center;padding:3rem;">'
            '<div style="font-size:2.5rem;margin-bottom:1rem;">&#128194;</div>'
            '<div style="font-size:1rem;font-weight:600;color:var(--text-primary);margin-bottom:0.5rem;">No Tenant Folders Yet</div>'
            '<div style="font-size:0.82rem;color:var(--text-tertiary);">Create a folder above, or generate a Lease Abstract and save it to a folder.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    # Display folders
    if folders:
        st.markdown("##### Tenant Folders")
        for folder_name in sorted(folders.keys()):
            docs = folders[folder_name]
            with st.expander("{} ({} documents)".format(folder_name, len(docs)), expanded=False):
                if not docs:
                    st.markdown(
                        '<div style="font-size:0.78rem;color:var(--text-muted);font-style:italic;">No documents yet. Generate a Lease Abstract and save it here.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    for i, doc in enumerate(docs):
                        dc1, dc2, dc3 = st.columns([3, 1, 1])
                        with dc1:
                            st.markdown(
                                '<div style="padding:0.5rem 0;border-bottom:1px solid var(--border);">'
                                '<div style="font-size:0.85rem;font-weight:600;color:var(--text-primary);">{}</div>'
                                '<div style="font-size:0.7rem;color:var(--text-muted);">{} | {}</div>'
                                '</div>'.format(doc["type"], doc["filename"], doc["date"]),
                                unsafe_allow_html=True,
                            )
                        with dc2:
                            docx_bytes = None
                            # Prefer the actual stored document (works for any type).
                            if doc.get("docx_b64"):
                                try:
                                    docx_bytes = base64.b64decode(doc["docx_b64"])
                                except Exception:
                                    docx_bytes = None
                            # Fall back to regenerating older abstracts from fields.
                            if docx_bytes is None and doc.get("fields") and doc.get("type") in ("Lease Abstract", "Lease Scan"):
                                try:
                                    from page_abstract import _generate_abstract_docx
                                    docx_bytes = _generate_abstract_docx(doc["fields"])
                                except Exception:
                                    docx_bytes = None
                            if docx_bytes is not None:
                                st.download_button(
                                    "Download", docx_bytes, doc["filename"], _DOCX_MIME,
                                    key="ten_dl_{}_{}".format(folder_name[:10], i),
                                )
                            else:
                                st.markdown('<div style="font-size:0.7rem;color:var(--text-muted);">-</div>', unsafe_allow_html=True)
                        with dc3:
                            if st.button("Remove", key="ten_rm_{}_{}".format(folder_name[:10], i)):
                                docs.pop(i)
                                shared_db.put("tenant_folders", folders)
                                st.rerun()

                # Delete folder button
                if st.button("Delete folder '{}'".format(folder_name), key="ten_del_{}".format(folder_name[:20])):
                    del folders[folder_name]
                    shared_db.put("tenant_folders", folders)
                    st.rerun()

    # Unassigned scans
    if scan_history:
        st.markdown("---")
        st.markdown("##### Recent Scans (not yet in folders)")
        for i, scan in enumerate(scan_history[:20]):
            sc1, sc2, sc3 = st.columns([3, 1, 1])
            with sc1:
                st.markdown(
                    '<div style="padding:0.4rem 0;border-bottom:1px solid var(--border);">'
                    '<div style="font-size:0.85rem;font-weight:600;color:var(--text-primary);">{}</div>'
                    '<div style="font-size:0.7rem;color:var(--text-muted);">{} | {} | Suite {}</div>'
                    '</div>'.format(
                        scan["tenant"], scan["filename"], scan["date"],
                        scan.get("suite", "-"),
                    ),
                    unsafe_allow_html=True,
                )
            with sc2:
                if folders:
                    target = st.selectbox(
                        "Folder", [""] + list(folders.keys()),
                        key="ten_assign_{}".format(i),
                    )
                else:
                    target = ""
            with sc3:
                if target and st.button("Add", key="ten_add_{}".format(i)):
                    entry = {
                        "type": "Lease Scan",
                        "tenant": scan["tenant"],
                        "filename": scan["filename"],
                        "date": scan["date"],
                        "fields": scan.get("fields", {}),
                    }
                    folders[target].append(entry)
                    shared_db.put("tenant_folders", folders)
                    st.success("Added to {}".format(target))
                    st.rerun()
