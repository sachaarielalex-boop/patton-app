"""Objective of the Month page – monthly sales targets per team member.

Each person has a monthly objective (goal) and a real production figure, plus a
personal to-do list. The team view aggregates every person's objective and real
production and shows the overall completion percentage. Data persists in
shared_db under the key "sales_objectives" so it is shared across users/devices.

Store shape:
    {
      "month": "2026-06",
      "people": [
        {"name": "Sacha", "objective": 1000000, "production": 900000,
         "done": False, "todos": [{"text": "...", "done": False}]},
        ...
      ]
    }
"""
import streamlit as st
import datetime
import shared_db

_DB_KEY = "sales_objectives"


def _get_store():
    store = shared_db.get(_DB_KEY, {})
    if not isinstance(store, dict):
        store = {}
    store.setdefault("people", [])
    store.setdefault("month", datetime.date.today().strftime("%Y-%m"))
    return store


def _save_store(store):
    shared_db.put(_DB_KEY, store)


def _fmt_money(n):
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "$0"
    if n >= 1_000_000:
        return "${:.2f}M".format(n / 1_000_000)
    if n >= 1_000:
        return "${:.0f}K".format(n / 1_000)
    return "${:.0f}".format(n)


def _pct(production, objective):
    try:
        objective = float(objective)
        if objective <= 0:
            return 0
        return max(0, min(100, round(float(production) / objective * 100)))
    except (TypeError, ValueError):
        return 0


def _progress_bar(pct, done=False):
    color = "var(--green)" if (done or pct >= 100) else "var(--accent)"
    return (
        '<div style="background:var(--bg-secondary);border-radius:99px;height:10px;overflow:hidden;margin:0.35rem 0;">'
        '<div style="width:{pct}%;height:100%;background:{color};border-radius:99px;transition:width .4s;"></div>'
        '</div>'.format(pct=pct, color=color)
    )


def render_sales_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="obj_back"):
        st.session_state["app_mode"] = "home"
        st.session_state.pop("obj_person", None)
        st.rerun()

    store = _get_store()

    # ── Sidebar: add a person (with objective) ──────────────
    st.sidebar.markdown("### Team")
    new_name = st.sidebar.text_input("Add a person", key="obj_new_name", placeholder="First name")
    new_obj = st.sidebar.number_input(
        "Their objective ($)", min_value=0, step=50000, value=0, key="obj_new_obj")
    if st.sidebar.button("+ Add person", key="obj_add_person", use_container_width=True, type="primary"):
        name = (new_name or "").strip()
        if name and not any(p["name"].lower() == name.lower() for p in store["people"]):
            store["people"].append({"name": name, "objective": int(new_obj), "production": 0, "done": False, "todos": []})
            _save_store(store)
            st.session_state["obj_person"] = name
            st.rerun()
    if store["people"]:
        st.sidebar.markdown("---")
        for p in store["people"]:
            if st.sidebar.button(p["name"], key="obj_side_" + p["name"], use_container_width=True):
                st.session_state["obj_person"] = p["name"]
                st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    month_label = _month_label(store["month"])
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.2rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);">Objective of the Month</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Monthly targets &amp; real production &mdash; {month}</div></div>'
        '</div>'.format(logo=logo_tag, month=month_label),
        unsafe_allow_html=True,
    )

    person = st.session_state.get("obj_person")
    if person and any(p["name"] == person for p in store["people"]):
        _render_person(store, person)
    else:
        st.session_state.pop("obj_person", None)
        _render_team(store)


def _month_label(ym):
    try:
        return datetime.datetime.strptime(ym, "%Y-%m").strftime("%B %Y")
    except Exception:
        return ym


def _render_team(store):
    people = store["people"]
    total_obj = sum(float(p.get("objective", 0) or 0) for p in people)
    total_prod = sum(float(p.get("production", 0) or 0) for p in people)
    team_pct = _pct(total_prod, total_obj)
    done_count = sum(1 for p in people if p.get("done"))

    # ── Team global view ────────────────────────────────────
    st.markdown(
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem;">'
        '<div class="kpi-card"><div class="kl">Team Members</div><div class="kv">{n}</div></div>'
        '<div class="kpi-card"><div class="kl">Team Objective</div><div class="kv">{obj}</div></div>'
        '<div class="kpi-card"><div class="kl">Real Production</div><div class="kv">{prod}</div></div>'
        '<div class="kpi-card"><div class="kl">Goals Reached</div><div class="kv">{done}/{n}</div></div>'
        '</div>'.format(n=len(people), obj=_fmt_money(total_obj), prod=_fmt_money(total_prod), done=done_count),
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="card" style="padding:1.2rem 1.4rem;margin-bottom:1.4rem;">'
        '<div style="display:flex;justify-content:space-between;align-items:baseline;">'
        '<div style="font-weight:800;color:var(--text-primary);">Team Progress</div>'
        '<div style="font-weight:900;font-size:1.4rem;color:{c};">{pct}%</div></div>'
        '{bar}'
        '<div style="font-size:0.78rem;color:var(--text-muted);">{prod} of {obj} target reached</div>'
        '</div>'.format(
            c="var(--green)" if team_pct >= 100 else "var(--accent)",
            pct=team_pct, bar=_progress_bar(team_pct, team_pct >= 100),
            prod=_fmt_money(total_prod), obj=_fmt_money(total_obj),
        ),
        unsafe_allow_html=True,
    )

    if not people:
        st.markdown(
            '<div class="card" style="text-align:center;padding:2.5rem;">'
            '<div style="font-size:2rem;margin-bottom:0.8rem;">&#128101;</div>'
            '<div style="font-size:0.9rem;font-weight:600;color:var(--text-primary);">No team members yet</div>'
            '<div style="font-size:0.8rem;color:var(--text-tertiary);margin-top:0.3rem;">'
            'Use &ldquo;Add a person&rdquo; in the left sidebar to get started.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown("##### Team members")
    for i in range(0, len(people), 2):
        cols = st.columns(2, gap="large")
        for ci, p in enumerate(people[i:i + 2]):
            pct = _pct(p.get("production", 0), p.get("objective", 0))
            with cols[ci]:
                with st.container(border=True):
                    check = "&#9989; " if p.get("done") else ""
                    st.markdown(
                        '<div style="padding:0.2rem 0.3rem;">'
                        '<div style="display:flex;justify-content:space-between;align-items:baseline;">'
                        '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);">{check}{name}</div>'
                        '<div style="font-weight:900;color:{c};">{pct}%</div></div>'
                        '{bar}'
                        '<div style="font-size:0.76rem;color:var(--text-muted);">'
                        'Goal {obj} &middot; Real {prod}</div>'
                        '</div>'.format(
                            check=check, name=p["name"],
                            c="var(--green)" if p.get("done") or pct >= 100 else "var(--accent)",
                            pct=pct, bar=_progress_bar(pct, p.get("done")),
                            obj=_fmt_money(p.get("objective", 0)), prod=_fmt_money(p.get("production", 0)),
                        ),
                        unsafe_allow_html=True,
                    )
                    if st.button("Open " + p["name"], key="obj_open_" + p["name"], use_container_width=True, type="primary"):
                        st.session_state["obj_person"] = p["name"]
                        st.rerun()


def _render_person(store, name):
    people = store["people"]
    idx = next(i for i, p in enumerate(people) if p["name"] == name)
    p = people[idx]

    if st.button("Back to Team", key="obj_person_back"):
        st.session_state.pop("obj_person", None)
        st.rerun()

    st.markdown("### {} &mdash; To-Do & Targets".format(name))

    # ── Objective / production inputs ───────────────────────
    c1, c2 = st.columns(2)
    with c1:
        objective = st.number_input(
            "Objective ($)", min_value=0, step=50000,
            value=int(float(p.get("objective", 0) or 0)), key="obj_obj_" + name,
        )
    with c2:
        production = st.number_input(
            "Real production ($)", min_value=0, step=50000,
            value=int(float(p.get("production", 0) or 0)), key="obj_prod_" + name,
        )

    pct = _pct(production, objective)
    st.markdown(
        '<div class="card" style="padding:1rem 1.3rem;margin:0.6rem 0 1rem;">'
        '<div style="display:flex;justify-content:space-between;align-items:baseline;">'
        '<div style="font-weight:800;color:var(--text-primary);">Progress</div>'
        '<div style="font-weight:900;font-size:1.3rem;color:{c};">{pct}%</div></div>'
        '{bar}'
        '<div style="font-size:0.78rem;color:var(--text-muted);">{prod} of {obj}</div>'
        '</div>'.format(
            c="var(--green)" if pct >= 100 else "var(--accent)", pct=pct,
            bar=_progress_bar(pct, p.get("done")), prod=_fmt_money(production), obj=_fmt_money(objective),
        ),
        unsafe_allow_html=True,
    )

    done = st.checkbox("Objective reached / completed", value=bool(p.get("done")), key="obj_done_" + name)

    if st.button("Save targets", key="obj_save_" + name, type="primary"):
        p["objective"] = objective
        p["production"] = production
        p["done"] = done
        _save_store(store)
        st.success("Saved.")
        st.rerun()

    st.markdown("---")

    # ── To-do list ──────────────────────────────────────────
    st.markdown("##### {}'s to-do list".format(name))
    todos = p.get("todos", [])
    for ti, todo in enumerate(todos):
        tc1, tc2 = st.columns([0.9, 0.1])
        with tc1:
            checked = st.checkbox(
                todo.get("text", ""), value=bool(todo.get("done")),
                key="obj_todo_{}_{}".format(name, ti),
            )
            if checked != bool(todo.get("done")):
                todo["done"] = checked
                _save_store(store)
                st.rerun()
        with tc2:
            if st.button("X", key="obj_todo_rm_{}_{}".format(name, ti)):
                todos.pop(ti)
                p["todos"] = todos
                _save_store(store)
                st.rerun()

    new_todo = st.text_input("Add a task", key="obj_new_todo_" + name, placeholder="e.g. Close Brickell deal")
    if st.button("+ Add task", key="obj_add_todo_" + name):
        txt = (new_todo or "").strip()
        if txt:
            todos.append({"text": txt, "done": False})
            p["todos"] = todos
            _save_store(store)
            st.rerun()

    st.markdown("---")
    if st.button("Remove " + name + " from team", key="obj_rmperson_" + name):
        people.pop(idx)
        _save_store(store)
        st.session_state.pop("obj_person", None)
        st.rerun()
