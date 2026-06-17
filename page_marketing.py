"""Marketing Folder page – brand assets organized by category (logos, images,
decks, media, case studies, videos). Uploaded files persist as base64 in shared_db
so they survive Streamlit Cloud's read-only filesystem. Bundled default assets
(e.g. the Patton logos) live in the repo under assets/<category>/ and always show."""
import streamlit as st
import os
import base64
import datetime
import shared_db

_DB_KEY = "marketing_files"
_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Categories that ship with bundled default files from the repo (assets/<subdir>/).
_DEFAULT_DIRS = {"logos": "logos", "decks": "decks"}

# (key, icon, label, description)
CATEGORIES = [
    ("logos", "&#127991;", "Logos", "Patton logos &mdash; primary, mono, icon, variations."),
    ("images", "&#128247;", "Images", "Photography, building shots, headshots, stock imagery."),
    ("decks", "&#128202;", "Presentation Decks", "Pitch decks, listing presentations, capability decks."),
    ("media", "&#128226;", "Media", "Press mentions, brochures, flyers, social graphics."),
    ("case_studies", "&#128218;", "Case Studies", "Deal write-ups, success stories, tenant testimonials."),
    ("videos", "&#127909;", "Videos", "Property tours, promo reels, drone footage."),
]
_CAT_LABEL = {k: lbl for k, _, lbl, _ in CATEGORIES}

_IMAGE_EXT = ("png", "jpg", "jpeg", "gif", "webp", "svg")
_VIDEO_EXT = ("mp4", "mov", "webm", "m4v")


def _get_store():
    return shared_db.get(_DB_KEY, {})


def _save_store(store):
    shared_db.put(_DB_KEY, store)


def _add_files(category, uploaded_files):
    store = _get_store()
    bucket = store.get(category, [])
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
    store[category] = bucket
    _save_store(store)
    return added


def _fmt_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return "{:.0f} {}".format(n, unit)
        n /= 1024.0
    return "{:.1f} TB".format(n)


def _default_files(category):
    """Bundled repo assets for a category, as (name, bytes). Empty if none."""
    sub = _DEFAULT_DIRS.get(category)
    if not sub:
        return []
    d = os.path.join(_ASSETS_DIR, sub)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        path = os.path.join(d, name)
        if name.startswith(".") or not os.path.isfile(path):
            continue
        try:
            with open(path, "rb") as fh:
                out.append((name, fh.read()))
        except Exception:
            continue
    return out


def _category_count(category, store):
    return len(store.get(category, [])) + len(_default_files(category))


def render_marketing_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="mkt_back"):
        st.session_state["app_mode"] = "home"
        st.session_state.pop("mkt_category", None)
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Marketing Folder</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Brand assets, decks, media &amp; case studies</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    cat = st.session_state.get("mkt_category")
    if cat and cat in _CAT_LABEL:
        _render_category(cat)
    else:
        _render_landing()


def _render_landing():
    store = _get_store()
    total = sum(len(v) for v in store.values())
    st.markdown(
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem;">'
        '<div class="kpi-card"><div class="kl">Categories</div><div class="kv">{}</div></div>'
        '<div class="kpi-card"><div class="kl">Total Files</div><div class="kv">{}</div></div>'
        '</div>'.format(len(CATEGORIES), total),
        unsafe_allow_html=True,
    )

    st.markdown("##### Select a category")
    for row_start in (0, 2, 4):
        cols = st.columns(2, gap="large")
        for ci, (key, icon, label, desc) in enumerate(CATEGORIES[row_start:row_start + 2]):
            count = _category_count(key, store)
            with cols[ci]:
                with st.container(border=True):
                    st.markdown(
                        '<div class="mod-inner">'
                        '<div class="mod-icon" style="background:var(--accent-soft);border:1px solid var(--accent-border);">{icon}</div>'
                        '<div style="font-size:1.02rem;font-weight:800;color:var(--text-primary);margin-bottom:0.4rem;">{label}</div>'
                        '<p style="font-size:0.74rem;color:var(--text-tertiary);line-height:1.6;margin:0 0 0.7rem;">{desc}</p>'
                        '<div style="display:flex;justify-content:center;">'
                        '<span class="badge badge-blue">{count} files</span></div>'
                        '</div>'.format(icon=icon, label=label, desc=desc, count=count),
                        unsafe_allow_html=True,
                    )
                    if st.button("Open " + label, use_container_width=True, key="mkt_open_" + key, type="primary"):
                        st.session_state["mkt_category"] = key
                        st.rerun()


def _render_category(cat):
    if st.button("Back to Marketing", key="mkt_cat_back"):
        st.session_state.pop("mkt_category", None)
        st.rerun()

    label = _CAT_LABEL[cat]
    st.markdown("### {}".format(label))

    # Uploader
    uploaded = st.file_uploader(
        "Add documents to {}".format(label),
        accept_multiple_files=True,
        key="mkt_upload_" + cat,
    )
    if uploaded and st.button("Upload {} file(s)".format(len(uploaded)), key="mkt_do_upload_" + cat, type="primary"):
        added = _add_files(cat, uploaded)
        st.success("Added {} file(s) to {}.".format(added, label))
        st.rerun()

    st.markdown("---")

    # Bundled Patton brand assets (shipped with the app, always available)
    defaults = _default_files(cat)
    if defaults:
        st.markdown("##### Patton brand assets")
        for di, (name, data) in enumerate(defaults):
            ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            with st.container(border=True):
                dc1, dc2 = st.columns([3, 1])
                with dc1:
                    st.markdown(
                        '<div style="font-size:0.88rem;font-weight:700;color:var(--text-primary);">{}</div>'
                        '<div style="font-size:0.7rem;color:var(--text-muted);">{} | bundled</div>'.format(
                            name, _fmt_size(len(data))
                        ),
                        unsafe_allow_html=True,
                    )
                with dc2:
                    st.download_button(
                        "Download", data, name, "image/png" if ext == "png" else "application/octet-stream",
                        key="mkt_def_dl_{}_{}".format(cat, di), use_container_width=True,
                    )
                if ext in _IMAGE_EXT and ext != "svg":
                    st.image(data, width=260)
                elif ext == "svg":
                    st.markdown(data.decode("utf-8", "ignore"), unsafe_allow_html=True)
        st.markdown("---")

    store = _get_store()
    files = store.get(cat, [])
    if not files and not defaults:
        st.markdown(
            '<div class="card" style="text-align:center;padding:2.5rem;">'
            '<div style="font-size:2rem;margin-bottom:0.8rem;">&#128193;</div>'
            '<div style="font-size:0.9rem;font-weight:600;color:var(--text-primary);">No files yet</div>'
            '<div style="font-size:0.8rem;color:var(--text-tertiary);margin-top:0.3rem;">Upload your first {} above.</div>'
            '</div>'.format(label.lower()),
            unsafe_allow_html=True,
        )
        return

    if not files:
        return

    st.markdown("##### Uploaded files ({})".format(len(files)))
    for i, f in enumerate(files):
        try:
            data = base64.b64decode(f["b64"])
        except Exception:
            data = b""
        ext = f["name"].rsplit(".", 1)[-1].lower() if "." in f["name"] else ""

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
                        key="mkt_dl_{}_{}".format(cat, i), use_container_width=True,
                    )
            with c3:
                if st.button("Remove", key="mkt_rm_{}_{}".format(cat, i), use_container_width=True):
                    files.pop(i)
                    store[cat] = files
                    _save_store(store)
                    st.rerun()

            # Inline preview for images / videos
            if data:
                if ext in _IMAGE_EXT and ext != "svg":
                    st.image(data, use_container_width=True)
                elif ext == "svg":
                    st.markdown(data.decode("utf-8", "ignore"), unsafe_allow_html=True)
                elif ext in _VIDEO_EXT:
                    st.video(data)
