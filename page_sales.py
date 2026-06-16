"""Sales Folder page – sales reports organized by year (2000-2030). Files persist
as base64 in shared_db so they survive Streamlit Cloud's read-only filesystem."""
import streamlit as st
import base64
import datetime
import shared_db

_DB_KEY = "sales_files"
YEARS = [str(y) for y in range(2000, 2031)]


def _get_store():
    return shared_db.get(_DB_KEY, {})


def _save_store(store):
    shared_db.put(_DB_KEY, store)


def _add_files(year, uploaded_files):
    store = _get_store()
    bucket = store.get(year, [])
    existing = {f["name"] for f in bucket}
    added = 0
    for uf in uploaded_files:
        if uf.name in existing:
            continue
        data = uf.getvalue()
        bucket.append({
            "name": uf.name,
            "mime": uf.type or "application/octet-stream",
            "size": len(data),
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "b64": base64.b64encode(data).decode("ascii"),
        })
        existing.add(uf.name)
        added += 1
    store[year] = bucket
    _save_store(store)
    return added


def _fmt_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return "{:.0f} {}".format(n, unit)
        n /= 1024.0
    return "{:.1f} TB".format(n)


def render_sales_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="sales_back"):
        st.session_state["app_mode"] = "home"
        st.session_state.pop("sales_year", None)
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Sales Folder</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Sales reports organized by year</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    year = st.session_state.get("sales_year")
    if year and year in YEARS:
        _render_year(year)
    else:
        _render_landing()


def _render_landing():
    store = _get_store()
    total = sum(len(v) for v in store.values())
    years_with = sum(1 for y in YEARS if store.get(y))
    st.markdown(
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem;">'
        '<div class="kpi-card"><div class="kl">Report Years</div><div class="kv">{}&ndash;{}</div></div>'
        '<div class="kpi-card"><div class="kl">Years with Reports</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Total Reports</div><div class="kv">{}</div></div>'
        '</div>'.format(YEARS[0], YEARS[-1], years_with, total),
        unsafe_allow_html=True,
    )

    st.markdown("##### Select a report year")
    # Newest first, 5 per row
    ordered = list(reversed(YEARS))
    per_row = 5
    for r in range(0, len(ordered), per_row):
        cols = st.columns(per_row, gap="small")
        for ci, y in enumerate(ordered[r:r + per_row]):
            count = len(store.get(y, []))
            with cols[ci]:
                with st.container(border=True):
                    badge = '<span class="badge badge-green">{} docs</span>'.format(count) if count else '<span class="badge" style="background:var(--bg-secondary);color:var(--text-muted);">empty</span>'
                    st.markdown(
                        '<div class="qa-inner">'
                        '<div style="font-size:1.15rem;font-weight:800;color:var(--text-primary);">{}</div>'
                        '<div style="margin-top:0.25rem;">{}</div>'
                        '</div>'.format(y, badge),
                        unsafe_allow_html=True,
                    )
                    if st.button("Open", use_container_width=True, key="sales_open_" + y):
                        st.session_state["sales_year"] = y
                        st.rerun()


def _render_year(year):
    if st.button("Back to Sales", key="sales_year_back"):
        st.session_state.pop("sales_year", None)
        st.rerun()

    st.markdown("### {} Sales Reports".format(year))

    uploaded = st.file_uploader(
        "Add documents to {}".format(year),
        accept_multiple_files=True,
        key="sales_upload_" + year,
    )
    if uploaded and st.button("Upload {} file(s)".format(len(uploaded)), key="sales_do_upload_" + year, type="primary"):
        added = _add_files(year, uploaded)
        st.success("Added {} file(s) to {}.".format(added, year))
        st.rerun()

    st.markdown("---")

    store = _get_store()
    files = store.get(year, [])
    if not files:
        st.markdown(
            '<div class="card" style="text-align:center;padding:2.5rem;">'
            '<div style="font-size:2rem;margin-bottom:0.8rem;">&#128202;</div>'
            '<div style="font-size:0.9rem;font-weight:600;color:var(--text-primary);">No reports for {}</div>'
            '<div style="font-size:0.8rem;color:var(--text-tertiary);margin-top:0.3rem;">Upload your first {} report above.</div>'
            '</div>'.format(year, year),
            unsafe_allow_html=True,
        )
        return

    st.markdown("##### {} documents".format(len(files)))
    for i, f in enumerate(files):
        try:
            data = base64.b64decode(f["b64"])
        except Exception:
            data = b""
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(
                    '<div style="font-size:0.88rem;font-weight:700;color:var(--text-primary);">{}</div>'
                    '<div style="font-size:0.7rem;color:var(--text-muted);">{} | {}</div>'.format(
                        f["name"], _fmt_size(f["size"]), f["date"]
                    ),
                    unsafe_allow_html=True,
                )
            with c2:
                if data:
                    st.download_button(
                        "Download", data, f["name"], f.get("mime", "application/octet-stream"),
                        key="sales_dl_{}_{}".format(year, i), use_container_width=True,
                    )
            with c3:
                if st.button("Remove", key="sales_rm_{}_{}".format(year, i), use_container_width=True):
                    files.pop(i)
                    store[year] = files
                    _save_store(store)
                    st.rerun()
