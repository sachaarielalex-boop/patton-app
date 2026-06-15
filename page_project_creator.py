"""Project Studio — step-by-step development designer with live 3D site plan."""
import streamlit as st
import math
import datetime
import shared_db
from utils.devplan import compute_dev_plan
from utils.property_data import format_currency

STEPS = ["Site", "Zoning", "Program", "Review"]

DEFAULTS = {
    "name": "",
    "address": "",
    "lat": 25.7617, "lon": -80.1918,
    "zoning": "",
    "lot_sf": 5000, "far": 3.5, "max_ht": 65, "max_fl": 5,
    "floor_eff": 80, "rent_eff": 85,
    "res_pct": 85, "office_pct": 10, "retail_pct": 5,
    "avg_unit_sf": 850, "parking_ratio": 1.0,
    "construction_psf": 250, "soft_cost_pct": 25,
    "land_price": 0, "target_rent_res": 2500,
    "target_rent_office": 35, "target_rent_retail": 40,
    "exit_cap": 5.0, "interest_rate": 7.0, "ltv": 65,
}


def _init_state():
    if "_proj" not in st.session_state:
        proj = dict(DEFAULTS)
        seed = st.session_state.pop("_project_seed", None)
        if seed:
            for k, v in seed.items():
                if v is not None and k in proj:
                    proj[k] = v
            if seed.get("lat") is None:
                proj["lat"] = DEFAULTS["lat"]
                proj["lon"] = DEFAULTS["lon"]
            if seed.get("address") and not proj["name"]:
                proj["name"] = seed["address"]
        st.session_state["_proj"] = proj
    if "_proj_step" not in st.session_state:
        st.session_state["_proj_step"] = 0


def _compute(p):
    return compute_dev_plan({
        "lot_sf": p["lot_sf"], "far": p["far"], "max_height_ft": p["max_ht"],
        "max_floors": p["max_fl"], "floor_efficiency": p["floor_eff"] / 100.0,
        "rentable_efficiency": p["rent_eff"] / 100.0, "avg_unit_sf": p["avg_unit_sf"],
        "res_pct": p["res_pct"], "office_pct": p["office_pct"], "retail_pct": p["retail_pct"],
        "parking_ratio": p["parking_ratio"], "construction_psf": p["construction_psf"],
        "soft_cost_pct": p["soft_cost_pct"], "land_price": p["land_price"],
        "target_rent_res": p["target_rent_res"], "target_rent_office": p["target_rent_office"],
        "target_rent_retail": p["target_rent_retail"], "exit_cap": p["exit_cap"],
        "interest_rate": p["interest_rate"], "ltv": p["ltv"], "opex_ratio": 35,
    })


def _stepper_html(active):
    items = ""
    for i, name in enumerate(STEPS):
        if i < active:
            state, bg, col, brd = "done", "var(--accent)", "#fff", "var(--accent)"
            inner = "&#10003;"
        elif i == active:
            state, bg, col, brd = "active", "var(--accent)", "#fff", "var(--accent)"
            inner = str(i + 1)
        else:
            state, bg, col, brd = "todo", "var(--bg-card)", "var(--text-muted)", "var(--border)"
            inner = str(i + 1)
        items += (
            '<div style="display:flex;flex-direction:column;align-items:center;flex:1;min-width:60px;">'
            '<div style="width:34px;height:34px;border-radius:50%;background:{bg};color:{col};'
            'border:2px solid {brd};display:flex;align-items:center;justify-content:center;'
            'font-weight:800;font-size:0.85rem;transition:all 0.3s ease;">{inner}</div>'
            '<div style="font-size:0.6rem;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;'
            'margin-top:0.4rem;color:{txt};">{name}</div>'
            '</div>'.format(
                bg=bg, col=col, brd=brd, inner=inner, name=name,
                txt="var(--text-primary)" if i <= active else "var(--text-muted)",
            )
        )
        if i < len(STEPS) - 1:
            line_col = "var(--accent)" if i < active else "var(--border)"
            items += (
                '<div style="flex:0.6;height:2px;background:{};margin:17px -4px 0;'
                'transition:background 0.3s ease;"></div>'.format(line_col)
            )
    return (
        '<div style="display:flex;align-items:flex-start;justify-content:center;'
        'max-width:600px;margin:0 auto 1.5rem;">{}</div>'.format(items)
    )


def _rect(lat, lon, side_ft):
    """Square footprint (side in feet) returned as polygon ring of [lon, lat] points."""
    half = side_ft / 2.0
    dlat = half / 364000.0
    dlon = half / (364000.0 * max(math.cos(math.radians(lat)), 0.01))
    return [
        [lon - dlon, lat - dlat],
        [lon + dlon, lat - dlat],
        [lon + dlon, lat + dlat],
        [lon - dlon, lat + dlat],
        [lon - dlon, lat - dlat],
    ]


def _massing_deck(p, dp):
    try:
        import pydeck as pdk
    except ImportError:
        return None
    lat, lon = p["lat"], p["lon"]
    # ft -> meters for extrusion, slightly exaggerated for a clear massing read.
    HSCALE = 0.45
    lot_side = math.sqrt(max(p["lot_sf"], 100))
    bld_side = math.sqrt(max(dp["floor_plate"], 100))
    over = dp["building_height_ft"] > p["max_ht"]
    bld_color = [220, 38, 38, 225] if over else [37, 99, 235, 225]

    lot = [{"polygon": _rect(lat, lon, lot_side), "name": "Lot Boundary"}]
    building = [{
        "polygon": _rect(lat, lon, bld_side),
        "elev": dp["building_height_ft"] * HSCALE,
        "color": bld_color, "name": "Proposed Building",
        "ht": dp["building_height_ft"], "fl": dp["est_floors"],
    }]
    envelope = [{
        "polygon": _rect(lat, lon, lot_side * 0.96),
        "elev": p["max_ht"] * HSCALE,
        "name": "Zoning Envelope", "ht": p["max_ht"], "fl": "-",
    }]

    lot_layer = pdk.Layer(
        "PolygonLayer", data=lot, get_polygon="polygon", extruded=False,
        stroked=True, filled=True, get_fill_color=[148, 163, 184, 55],
        get_line_color=[100, 116, 139, 200], line_width_min_pixels=2, pickable=False,
    )
    env_layer = pdk.Layer(
        "PolygonLayer", data=envelope, get_polygon="polygon", extruded=True,
        get_elevation="elev", wireframe=True, filled=True,
        get_fill_color=[220, 38, 38, 22], get_line_color=[220, 38, 38, 170],
        line_width_min_pixels=1, pickable=True,
    )
    bld_layer = pdk.Layer(
        "PolygonLayer", data=building, get_polygon="polygon", extruded=True,
        get_elevation="elev", wireframe=True, filled=True,
        get_fill_color="color", get_line_color=[255, 255, 255, 120],
        line_width_min_pixels=1, pickable=True,
    )
    view = pdk.ViewState(latitude=lat, longitude=lon, zoom=17.5, pitch=58, bearing=-25)
    return pdk.Deck(
        layers=[lot_layer, env_layer, bld_layer], initial_view_state=view,
        map_style="light",
        tooltip={"text": "{name}\n{ht} ft \u00b7 {fl} floors"},
    )


def _live_panel(p, dp):
    """Right-side live metrics + 3D massing."""
    over = dp["building_height_ft"] > p["max_ht"]
    over_gsf = dp["actual_gsf"] > dp["max_gsf"] + 1
    st.markdown(
        '<div style="font-size:0.7rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;'
        'color:var(--text-muted);margin-bottom:0.5rem;">Live 3D Site Plan</div>',
        unsafe_allow_html=True,
    )
    deck = _massing_deck(p, dp)
    if deck is not None:
        st.pydeck_chart(deck)
    st.markdown(
        '<div style="display:flex;gap:1rem;font-size:0.68rem;margin:0.4rem 0 0.8rem;">'
        '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;'
        'background:rgba(37,99,235,0.8);margin-right:4px;"></span>Proposed</span>'
        '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;'
        'background:rgba(220,38,38,0.3);margin-right:4px;"></span>Zoning Limit</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Compliance banner
    if over or over_gsf:
        msgs = []
        if over:
            msgs.append("Height {} ft exceeds zoning {} ft".format(dp["building_height_ft"], p["max_ht"]))
        if over_gsf:
            msgs.append("GSF exceeds max buildable")
        st.markdown(
            '<div class="alert-warn">&#9888; {}</div>'.format(" &middot; ".join(msgs)),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="alert-ok">&#10003; Within zoning envelope</div>',
            unsafe_allow_html=True,
        )

    profit_col = "var(--green)" if dp["profit"] > 0 else "var(--red)"
    cards = (
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;margin-top:0.4rem;">'
        '<div class="kpi-card"><div class="kl">Buildable GSF</div><div class="kv">{gsf}</div>'
        '<div class="ks">{fl} floors &middot; {ht} ft</div></div>'
        '<div class="kpi-card"><div class="kl">Est. Units</div><div class="kv">{units}</div>'
        '<div class="ks">{unit} sf avg</div></div>'
        '<div class="kpi-card"><div class="kl">Total Cost</div><div class="kv">{cost}</div>'
        '<div class="ks">All-in</div></div>'
        '<div class="kpi-card"><div class="kl">Profit</div>'
        '<div class="kv" style="color:{pcol};">{profit}</div>'
        '<div class="ks">{margin:.1f}% margin</div></div>'
        '</div>'
    ).format(
        gsf="{:,}".format(dp["actual_gsf"]), fl=dp["est_floors"], ht=dp["building_height_ft"],
        units=dp["est_units"], unit=dp["avg_unit_sf"],
        cost=format_currency(dp["total_dev_cost"]), profit=format_currency(dp["profit"]),
        pcol=profit_col, margin=dp["profit_margin"],
    )
    st.markdown(cards, unsafe_allow_html=True)


def _set(key):
    def _cb():
        st.session_state["_proj"][key] = st.session_state["pc_" + key]
    return _cb


def _num(label, key, p, step=1, minv=0, fmt=None):
    val = p[key]
    # Streamlit requires value/step/min_value to share the same numeric type.
    if isinstance(step, float) or isinstance(val, float) or isinstance(minv, float):
        val, step, minv = float(val), float(step), float(minv)
    else:
        val, step, minv = int(val), int(step), int(minv)
    st.number_input(
        label, value=val, step=step, min_value=minv,
        key="pc_" + key, on_change=_set(key),
    )


def render_project_creator():
    from utils.style import inject_css, LOGO_B64
    inject_css()
    _init_state()
    p = st.session_state["_proj"]
    step = st.session_state["_proj_step"]
    dp = _compute(p)

    # ── Header ──
    if st.sidebar.button("Back to Property Search", key="pc_back_prop"):
        st.session_state["app_mode"] = "property"
        st.rerun()
    if st.sidebar.button("Home", key="pc_home"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:46px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.2rem;">'
        '{logo}'
        '<div><h2 style="margin:0;color:var(--text-primary);letter-spacing:-0.5px;">Project Studio</h2>'
        '<div style="font-size:0.74rem;color:var(--text-muted);">'
        'Design your development step by step on a live 3D site plan</div></div>'
        '</div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    st.markdown(_stepper_html(step), unsafe_allow_html=True)

    left, right = st.columns([1, 1.15], gap="large")

    with left:
        if step == 0:
            st.markdown('<div class="card-title">Site Details</div>', unsafe_allow_html=True)
            p["name"] = st.text_input("Project Name", value=p["name"], key="pc_name_in",
                                      placeholder="e.g. Flagler Mixed-Use Tower")
            p["address"] = st.text_input("Site Address", value=p["address"], key="pc_addr_in",
                                         placeholder="858 W Flagler St, Miami, FL")
            _num("Lot Size (sqft)", "lot_sf", p, step=500, minv=500)
            c1, c2 = st.columns(2)
            with c1:
                p["lat"] = st.number_input("Latitude", value=float(p["lat"]),
                                           format="%.5f", key="pc_lat_in")
            with c2:
                p["lon"] = st.number_input("Longitude", value=float(p["lon"]),
                                           format="%.5f", key="pc_lon_in")
            _num("Land Price ($)", "land_price", p, step=10000, minv=0)

        elif step == 1:
            st.markdown('<div class="card-title">Zoning Restrictions</div>', unsafe_allow_html=True)
            p["zoning"] = st.text_input("Zoning Code", value=p["zoning"], key="pc_zone_in",
                                        placeholder="e.g. T6-8-O")
            _num("FAR (Floor Area Ratio)", "far", p, step=0.5, minv=0)
            _num("Max Height (ft)", "max_ht", p, step=5, minv=10)
            _num("Max Floors", "max_fl", p, step=1, minv=1)
            st.slider("Floor Efficiency %", 60, 95, p["floor_eff"], key="pc_floor_eff",
                      on_change=_set("floor_eff"))
            st.markdown(
                '<div class="alert-info">Max buildable: <b>{:,} sqft</b> &middot; '
                'Max envelope: <b>{} ft</b></div>'.format(int(dp["max_gsf"]), p["max_ht"]),
                unsafe_allow_html=True,
            )

        elif step == 2:
            st.markdown('<div class="card-title">Building Program</div>', unsafe_allow_html=True)
            st.slider("Rentable Efficiency %", 70, 95, p["rent_eff"], key="pc_rent_eff",
                      on_change=_set("rent_eff"))
            _num("Avg Unit Size (sqft)", "avg_unit_sf", p, step=50, minv=300)
            st.markdown('<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;'
                        'letter-spacing:1px;color:var(--text-muted);margin:0.5rem 0 0.2rem;">Use Mix</div>',
                        unsafe_allow_html=True)
            st.slider("Residential %", 0, 100, p["res_pct"], key="pc_res_pct",
                      on_change=_set("res_pct"))
            st.slider("Office %", 0, 100, p["office_pct"], key="pc_office_pct",
                      on_change=_set("office_pct"))
            st.slider("Retail %", 0, 100, p["retail_pct"], key="pc_retail_pct",
                      on_change=_set("retail_pct"))
            total_mix = p["res_pct"] + p["office_pct"] + p["retail_pct"]
            if total_mix != 100:
                st.markdown(
                    '<div class="alert-warn">Use mix totals {}% (should be 100%)</div>'.format(total_mix),
                    unsafe_allow_html=True,
                )
            st.number_input("Parking Ratio (per unit)", value=float(p["parking_ratio"]),
                            step=0.25, min_value=0.0, key="pc_parking_ratio",
                            on_change=_set("parking_ratio"))
            _num("Construction $/sqft", "construction_psf", p, step=10, minv=100)
            _num("Target Rent (res $/mo)", "target_rent_res", p, step=100, minv=500)

        elif step == 3:
            st.markdown('<div class="card-title">Review &amp; Save</div>', unsafe_allow_html=True)
            rows = (
                '<table class="dtable">'
                '<tr><td class="dk">Project</td><td class="dv">{name}</td></tr>'
                '<tr><td class="dk">Address</td><td class="dv">{addr}</td></tr>'
                '<tr><td class="dk">Zoning</td><td class="dv">{zone}</td></tr>'
                '<tr><td class="dk">Lot Size</td><td class="dv">{lot:,} sf</td></tr>'
                '<tr><td class="dk">Buildable GSF</td><td class="dv">{gsf:,} sf</td></tr>'
                '<tr><td class="dk">Floors / Height</td><td class="dv">{fl} / {ht} ft</td></tr>'
                '<tr><td class="dk">Est. Units</td><td class="dv">{units}</td></tr>'
                '<tr><td class="dk">Use Mix</td><td class="dv">{res}% R &middot; {off}% O &middot; {ret}% Rt</td></tr>'
                '<tr><td class="dk">Total Dev Cost</td><td class="dv">{cost}</td></tr>'
                '<tr><td class="dk">Projected Profit</td><td class="dv">{profit} ({margin:.1f}%)</td></tr>'
                '<tr><td class="dk">Return on Cost</td><td class="dv">{roc:.1f}%</td></tr>'
                '</table>'
            ).format(
                name=p["name"] or "Untitled Project", addr=p["address"] or "-",
                zone=p["zoning"] or "-", lot=p["lot_sf"], gsf=dp["actual_gsf"],
                fl=dp["est_floors"], ht=dp["building_height_ft"], units=dp["est_units"],
                res=p["res_pct"], off=p["office_pct"], ret=p["retail_pct"],
                cost=format_currency(dp["total_dev_cost"]),
                profit=format_currency(dp["profit"]), margin=dp["profit_margin"],
                roc=dp["return_on_cost"],
            )
            st.markdown(rows, unsafe_allow_html=True)

            p["name"] = st.text_input("Confirm project name", value=p["name"] or (p["address"] or "Untitled Project"),
                                      key="pc_finalname")
            if st.button("Save Project", key="pc_save", type="primary", use_container_width=True):
                projects = shared_db.get("projects", [])
                entry = {
                    "name": p["name"] or "Untitled Project",
                    "address": p["address"],
                    "zoning": p["zoning"],
                    "saved": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "inputs": dict(p),
                    "summary": {
                        "gsf": dp["actual_gsf"], "floors": dp["est_floors"],
                        "height": dp["building_height_ft"], "units": dp["est_units"],
                        "total_cost": dp["total_dev_cost"], "profit": dp["profit"],
                        "margin": round(dp["profit_margin"], 1),
                    },
                }
                projects = [pr for pr in projects if pr.get("name") != entry["name"]]
                projects.insert(0, entry)
                shared_db.put("projects", projects)
                st.success("Project saved: {}".format(entry["name"]))
                st.balloons()

    with right:
        _live_panel(p, dp)

    # ── Navigation ──
    st.markdown('<div style="height:0.6rem;"></div>', unsafe_allow_html=True)
    nav1, nav2, nav3 = st.columns([1, 1, 1])
    with nav1:
        if step > 0:
            if st.button("Back", key="pc_nav_back", use_container_width=True):
                st.session_state["_proj_step"] = step - 1
                st.rerun()
    with nav3:
        if step < len(STEPS) - 1:
            if st.button("Next", key="pc_nav_next", type="primary", use_container_width=True):
                st.session_state["_proj_step"] = step + 1
                st.rerun()
