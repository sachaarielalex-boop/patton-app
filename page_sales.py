"""Objective of the Month – team sales performance tracker.

A full performance tracker giving the whole team at a glance: each member's
objective vs. real production, attainment %, deals closed, pipeline and status
(Goal reached / On track / Behind / At risk), a ranked leaderboard, a side-by-side
chart and the aggregate team numbers. Each member also keeps a personal to-do list.
Data persists in shared_db under "sales_objectives" (shared across users/devices).

Store shape:
    {
      "month": "2026-06",
      "people": [
        {"name": "Sacha", "objective": 1000000, "production": 900000,
         "deals": 3, "pipeline": 450000, "done": False,
         "todos": [{"text": "...", "done": False}]},
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
    # Backfill new fields on legacy records.
    for p in store["people"]:
        p.setdefault("deals", 0)
        p.setdefault("pipeline", 0)
        p.setdefault("done", False)
        p.setdefault("todos", [])
    return store


def _save_store(store):
    shared_db.put(_DB_KEY, store)


def _num(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _fmt_money(n):
    n = _num(n)
    if abs(n) >= 1_000_000:
        return "${:.2f}M".format(n / 1_000_000)
    if abs(n) >= 1_000:
        return "${:.0f}K".format(n / 1_000)
    return "${:.0f}".format(n)


def _pct(production, objective):
    objective = _num(objective)
    if objective <= 0:
        return 0
    return max(0, min(999, round(_num(production) / objective * 100)))


def _status(pct, done):
    """Return (label, color-var) for a performance level."""
    if done or pct >= 100:
        return ("Goal reached", "var(--green)")
    if pct >= 75:
        return ("On track", "var(--accent)")
    if pct >= 40:
        return ("Behind", "#d97706")
    return ("At risk", "var(--red)")


def _progress_bar(pct, color):
    width = min(100, pct)
    return (
        '<div style="background:var(--bg-secondary);border-radius:99px;height:9px;overflow:hidden;margin:0.35rem 0;">'
        '<div style="width:{w}%;height:100%;background:{color};border-radius:99px;transition:width .4s;"></div>'
        '</div>'.format(w=width, color=color)
    )


def render_sales_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="obj_back"):
        st.session_state["app_mode"] = "home"
        st.session_state.pop("obj_person", None)
        st.rerun()

    store = _get_store()

    # ── Sidebar: add a person (name + objective) ────────────
    st.sidebar.markdown("### Team")
    new_name = st.sidebar.text_input("Add a person", key="obj_new_name", placeholder="First name")
    new_obj = st.sidebar.number_input(
        "Their objective ($)", min_value=0, step=50000, value=0, key="obj_new_obj")
    if st.sidebar.button("+ Add member", key="obj_add_person", use_container_width=True, type="primary"):
        name = (new_name or "").strip()
        if name and not any(p["name"].lower() == name.lower() for p in store["people"]):
            store["people"].append({
                "name": name, "objective": int(new_obj), "production": 0,
                "deals": 0, "pipeline": 0, "done": False, "todos": [],
            })
            _save_store(store)
            st.session_state["obj_person"] = name
            st.rerun()
    if store["people"]:
        st.sidebar.markdown("---")
        st.sidebar.caption("Open a member")
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
        '<div style="font-size:0.75rem;color:var(--text-muted);">Team sales performance tracker &mdash; {month}</div></div>'
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

    total_obj = sum(_num(p.get("objective")) for p in people)
    total_prod = sum(_num(p.get("production")) for p in people)
    total_deals = sum(int(_num(p.get("deals"))) for p in people)
    total_pipe = sum(_num(p.get("pipeline")) for p in people)
    team_pct = _pct(total_prod, total_obj)
    gap = max(0, total_obj - total_prod)
    done_count = sum(1 for p in people if p.get("done") or _pct(p.get("production"), p.get("objective")) >= 100)

    # ── Headline KPIs ───────────────────────────────────────
    st.markdown(
        '<div style="display:flex;gap:0.8rem;flex-wrap:wrap;margin-bottom:1rem;">'
        '<div class="kpi-card"><div class="kl">Members</div><div class="kv">{n}</div></div>'
        '<div class="kpi-card"><div class="kl">Team Objective</div><div class="kv">{obj}</div></div>'
        '<div class="kpi-card"><div class="kl">Real Production</div><div class="kv">{prod}</div></div>'
        '<div class="kpi-card"><div class="kl">Attainment</div><div class="kv">{pct}%</div></div>'
        '<div class="kpi-card"><div class="kl">Gap to Goal</div><div class="kv">{gap}</div></div>'
        '<div class="kpi-card"><div class="kl">Deals Closed</div><div class="kv">{deals}</div></div>'
        '<div class="kpi-card"><div class="kl">Pipeline</div><div class="kv">{pipe}</div></div>'
        '<div class="kpi-card"><div class="kl">Goals Reached</div><div class="kv">{done}/{n}</div></div>'
        '</div>'.format(
            n=len(people), obj=_fmt_money(total_obj), prod=_fmt_money(total_prod),
            pct=team_pct, gap=_fmt_money(gap), deals=total_deals,
            pipe=_fmt_money(total_pipe), done=done_count,
        ),
        unsafe_allow_html=True,
    )

    # ── Team progress bar ───────────────────────────────────
    st.markdown(
        '<div class="card" style="padding:1.2rem 1.4rem;margin-bottom:1.4rem;">'
        '<div style="display:flex;justify-content:space-between;align-items:baseline;">'
        '<div style="font-weight:800;color:var(--text-primary);">Team Progress</div>'
        '<div style="font-weight:900;font-size:1.5rem;color:{c};">{pct}%</div></div>'
        '{bar}'
        '<div style="font-size:0.78rem;color:var(--text-muted);">{prod} of {obj} &middot; {gap} to go</div>'
        '</div>'.format(
            c="var(--green)" if team_pct >= 100 else "var(--accent)",
            pct=team_pct, bar=_progress_bar(team_pct, "var(--green)" if team_pct >= 100 else "var(--accent)"),
            prod=_fmt_money(total_prod), obj=_fmt_money(total_obj), gap=_fmt_money(gap),
        ),
        unsafe_allow_html=True,
    )

    if not people:
        st.markdown(
            '<div class="card" style="text-align:center;padding:2.5rem;">'
            '<div style="font-size:2rem;margin-bottom:0.8rem;">&#128202;</div>'
            '<div style="font-size:0.9rem;font-weight:600;color:var(--text-primary);">No team members yet</div>'
            '<div style="font-size:0.8rem;color:var(--text-tertiary);margin-top:0.3rem;">'
            'Add a member and their objective in the left sidebar to start tracking.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Objective vs Production chart (custom HTML bars) ────
    st.markdown("##### Objective vs. Real Production")
    scale = max([_num(p.get("objective")) for p in people] +
                [_num(p.get("production")) for p in people] + [1])
    rows_html = []
    for p in people:
        obj = _num(p.get("objective"))
        prod = _num(p.get("production"))
        ow = max(2, round(obj / scale * 100))
        pw = max(2, round(prod / scale * 100)) if prod else 0
        pcolor = "var(--green)" if (p.get("done") or (obj > 0 and prod >= obj)) else "var(--accent)"
        rows_html.append(
            '<div style="margin-bottom:1rem;">'
            '<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:0.3rem;">'
            '<span style="font-weight:700;color:var(--text-primary);">{name}</span>'
            '<span style="color:var(--text-muted);">{prodm} / {objm}</span></div>'
            # objective track
            '<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">'
            '<span style="width:74px;font-size:0.62rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;">Objective</span>'
            '<div style="flex:1;background:var(--bg-secondary);border-radius:99px;height:14px;overflow:hidden;">'
            '<div style="width:{ow}%;height:100%;background:#94a3b8;border-radius:99px;"></div></div></div>'
            # production track
            '<div style="display:flex;align-items:center;gap:0.5rem;">'
            '<span style="width:74px;font-size:0.62rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;">Production</span>'
            '<div style="flex:1;background:var(--bg-secondary);border-radius:99px;height:14px;overflow:hidden;">'
            '<div style="width:{pw}%;height:100%;background:{pcolor};border-radius:99px;transition:width .4s;"></div></div></div>'
            '</div>'.format(
                name=p["name"], prodm=_fmt_money(prod), objm=_fmt_money(obj),
                ow=ow, pw=pw, pcolor=pcolor,
            )
        )
    st.markdown(
        '<div class="card" style="padding:1.3rem 1.4rem;margin-bottom:1.4rem;">' + "".join(rows_html) + '</div>',
        unsafe_allow_html=True,
    )

    # ── Leaderboard (ranked by attainment) ──────────────────
    st.markdown("##### Leaderboard")
    ranked = sorted(
        people,
        key=lambda p: (_pct(p.get("production"), p.get("objective")), _num(p.get("production"))),
        reverse=True,
    )
    medals = {0: "&#129351;", 1: "&#129352;", 2: "&#129353;"}
    for rank, p in enumerate(ranked):
        pct = _pct(p.get("production"), p.get("objective"))
        label, color = _status(pct, p.get("done"))
        badge = medals.get(rank, '<span style="color:var(--text-muted);font-weight:800;">#{}</span>'.format(rank + 1))
        with st.container(border=True):
            st.markdown(
                '<div style="padding:0.2rem 0.3rem;">'
                '<div style="display:flex;justify-content:space-between;align-items:center;">'
                '<div style="display:flex;align-items:center;gap:0.6rem;">'
                '<div style="font-size:1.1rem;">{badge}</div>'
                '<div style="font-size:1.05rem;font-weight:800;color:var(--text-primary);">{name}</div>'
                '<span style="font-size:0.6rem;font-weight:700;padding:0.12rem 0.5rem;border-radius:20px;'
                'background:var(--bg-secondary);color:{color};border:1px solid var(--border);">{status}</span>'
                '</div>'
                '<div style="font-weight:900;font-size:1.15rem;color:{color};">{pct}%</div></div>'
                '{bar}'
                '<div style="display:flex;gap:1.2rem;font-size:0.74rem;color:var(--text-muted);flex-wrap:wrap;">'
                '<span>Goal <b style="color:var(--text-secondary);">{obj}</b></span>'
                '<span>Real <b style="color:var(--text-secondary);">{prod}</b></span>'
                '<span>Deals <b style="color:var(--text-secondary);">{deals}</b></span>'
                '<span>Pipeline <b style="color:var(--text-secondary);">{pipe}</b></span>'
                '</div></div>'.format(
                    badge=badge, name=p["name"], color=color, status=label, pct=pct,
                    bar=_progress_bar(pct, color),
                    obj=_fmt_money(p.get("objective")), prod=_fmt_money(p.get("production")),
                    deals=int(_num(p.get("deals"))), pipe=_fmt_money(p.get("pipeline")),
                ),
                unsafe_allow_html=True,
            )
            if st.button("Open " + p["name"], key="obj_open_" + p["name"], use_container_width=True):
                st.session_state["obj_person"] = p["name"]
                st.rerun()


def _render_person(store, name):
    people = store["people"]
    idx = next(i for i, p in enumerate(people) if p["name"] == name)
    p = people[idx]

    if st.button("Back to Team", key="obj_person_back"):
        st.session_state.pop("obj_person", None)
        st.rerun()

    pct = _pct(p.get("production"), p.get("objective"))
    label, color = _status(pct, p.get("done"))
    st.markdown(
        '<div style="display:flex;align-items:center;gap:0.7rem;margin:0.4rem 0 0.2rem;">'
        '<h3 style="margin:0;color:var(--text-primary);">{name}</h3>'
        '<span style="font-size:0.65rem;font-weight:700;padding:0.15rem 0.6rem;border-radius:20px;'
        'background:var(--bg-secondary);color:{color};border:1px solid var(--border);">{status}</span>'
        '</div>'.format(name=name, color=color, status=label),
        unsafe_allow_html=True,
    )

    # ── Performance inputs ──────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        objective = st.number_input(
            "Objective ($)", min_value=0, step=50000,
            value=int(_num(p.get("objective"))), key="obj_obj_" + name)
        deals = st.number_input(
            "Deals closed", min_value=0, step=1,
            value=int(_num(p.get("deals"))), key="obj_deals_" + name)
    with c2:
        production = st.number_input(
            "Real production ($)", min_value=0, step=50000,
            value=int(_num(p.get("production"))), key="obj_prod_" + name)
        pipeline = st.number_input(
            "Pipeline ($)", min_value=0, step=50000,
            value=int(_num(p.get("pipeline"))), key="obj_pipe_" + name)

    live_pct = _pct(production, objective)
    live_label, live_color = _status(live_pct, p.get("done"))
    gap = max(0, objective - production)
    avg_deal = (production / deals) if deals else 0
    st.markdown(
        '<div class="card" style="padding:1rem 1.3rem;margin:0.6rem 0 1rem;">'
        '<div style="display:flex;justify-content:space-between;align-items:baseline;">'
        '<div style="font-weight:800;color:var(--text-primary);">Performance &mdash; {status}</div>'
        '<div style="font-weight:900;font-size:1.4rem;color:{c};">{pct}%</div></div>'
        '{bar}'
        '<div style="display:flex;gap:1.4rem;font-size:0.76rem;color:var(--text-muted);flex-wrap:wrap;margin-top:0.3rem;">'
        '<span>Real <b style="color:var(--text-secondary);">{prod}</b> of <b style="color:var(--text-secondary);">{obj}</b></span>'
        '<span>Gap <b style="color:var(--text-secondary);">{gap}</b></span>'
        '<span>Avg deal <b style="color:var(--text-secondary);">{avg}</b></span>'
        '</div></div>'.format(
            status=live_label, c=live_color, pct=live_pct,
            bar=_progress_bar(live_pct, live_color),
            prod=_fmt_money(production), obj=_fmt_money(objective),
            gap=_fmt_money(gap), avg=_fmt_money(avg_deal),
        ),
        unsafe_allow_html=True,
    )

    done = st.checkbox("Objective reached / completed", value=bool(p.get("done")), key="obj_done_" + name)

    if st.button("Save performance", key="obj_save_" + name, type="primary"):
        p["objective"] = objective
        p["production"] = production
        p["deals"] = deals
        p["pipeline"] = pipeline
        p["done"] = done
        _save_store(store)
        st.success("Saved.")
        st.rerun()

    st.markdown("---")

    # ── To-do list ──────────────────────────────────────────
    todos = p.get("todos", [])
    done_tasks = sum(1 for t in todos if t.get("done"))
    st.markdown("##### {}'s to-do list &nbsp;<span style='font-size:0.78rem;color:var(--text-muted);'>{}/{} done</span>".format(
        name, done_tasks, len(todos)), unsafe_allow_html=True)
    for ti, todo in enumerate(todos):
        tc1, tc2 = st.columns([0.9, 0.1])
        with tc1:
            checked = st.checkbox(
                todo.get("text", ""), value=bool(todo.get("done")),
                key="obj_todo_{}_{}".format(name, ti))
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
