"""Project Studio — step-by-step development designer with live 3D site plan."""
import streamlit as st
import math
import datetime
import shared_db
from utils.devplan import compute_dev_plan, scenario_comparison
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
    HSCALE = 0.3048  # feet -> meters: true-scale so proportions look like a real building
    lot_side = math.sqrt(max(p["lot_sf"], 100))
    over = dp["building_height_ft"] > p["max_ht"]
    bld_color = [220, 38, 38, 235] if over else [37, 99, 235, 235]
    # Building covers ~88% of the lot (typical setback).
    bld_side = lot_side * 0.88

    lot = [{"polygon": _rect(lat, lon, lot_side), "name": "Lot Boundary"}]
    building = [{
        "polygon": _rect(lat, lon, bld_side),
        "elev": dp["building_height_ft"] * HSCALE,
        "color": bld_color, "name": "Proposed Building",
        "ht": dp["building_height_ft"], "fl": dp["est_floors"],
    }]
    envelope = [{
        "polygon": _rect(lat, lon, lot_side),
        "elev": p["max_ht"] * HSCALE,
        "name": "Zoning Envelope", "ht": p["max_ht"], "fl": "limit",
    }]

    lot_layer = pdk.Layer(
        "PolygonLayer", data=lot, get_polygon="polygon", extruded=False,
        stroked=True, filled=True, get_fill_color=[148, 163, 184, 70],
        get_line_color=[71, 85, 105, 220], line_width_min_pixels=2, pickable=False,
    )
    env_layer = pdk.Layer(
        "PolygonLayer", data=envelope, get_polygon="polygon", extruded=True,
        get_elevation="elev", wireframe=True, filled=True,
        get_fill_color=[220, 38, 38, 8], get_line_color=[220, 38, 38, 130],
        line_width_min_pixels=1, pickable=True,
    )
    bld_layer = pdk.Layer(
        "PolygonLayer", data=building, get_polygon="polygon", extruded=True,
        get_elevation="elev", wireframe=True, filled=True,
        get_fill_color="color", get_line_color=[255, 255, 255, 90],
        line_width_min_pixels=1, pickable=True,
    )
    view = pdk.ViewState(latitude=lat, longitude=lon, zoom=17.2, pitch=52, bearing=-22)
    return pdk.Deck(
        layers=[lot_layer, env_layer, bld_layer], initial_view_state=view,
        map_style="road",
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


def _step_html(num, title, formula, note):
    return (
        '<div style="display:flex;gap:0.8rem;padding:0.9rem 0;border-bottom:1px solid var(--border);">'
        '<div style="flex:0 0 26px;height:26px;border-radius:50%;background:var(--accent);color:#fff;'
        'display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.8rem;">{num}</div>'
        '<div style="flex:1;">'
        '<div style="font-size:0.86rem;font-weight:800;color:var(--text-primary);margin-bottom:0.2rem;">{title}</div>'
        '<div style="font-size:0.82rem;color:var(--text-secondary);font-family:ui-monospace,Menlo,monospace;'
        'background:var(--bg-subtle,rgba(37,99,235,0.05));border-radius:8px;padding:0.4rem 0.6rem;margin:0.25rem 0;">{formula}</div>'
        '<div style="font-size:0.74rem;color:var(--text-muted);line-height:1.5;">{note}</div>'
        '</div></div>'
    ).format(num=num, title=title, formula=formula, note=note)


def _verdict(p, dp):
    """Return (label, color_var, bg_var, rationale) investment recommendation."""
    margin = dp["profit_margin"]
    dscr = dp["dscr"]
    spread = dp["return_on_cost"] - p.get("exit_cap", 5.0)  # development spread, %
    if margin >= 15 and dscr >= 1.25 and spread >= 1.0:
        return ("PROCEED", "var(--green)", "var(--green-soft)",
                "Strong margin, healthy debt coverage and a development spread above the market cap rate.")
    if margin >= 5 and dscr >= 1.10:
        return ("PROCEED WITH CAUTION", "var(--amber)", "var(--amber-soft)",
                "Returns are positive but thin &mdash; the deal is sensitive to cost overruns, rent softness or cap-rate expansion.")
    return ("DO NOT PROCEED", "var(--red)", "var(--red-soft)",
            "Projected returns and/or debt coverage fall below institutional thresholds at these assumptions.")


def _exec_summary_html(p, dp):
    """Top-of-memo headline: verdict banner + the four numbers a principal reads first."""
    fc = format_currency
    label, col, bg, rationale = _verdict(p, dp)
    spread = dp["return_on_cost"] - p.get("exit_cap", 5.0)
    pcol = "var(--green)" if dp["profit"] > 0 else "var(--red)"
    metrics = [
        ("Total Capitalization", fc(dp["total_dev_cost"]), "All-in cost to build", "var(--text-primary)"),
        ("Stabilized Value", fc(dp["value_at_cap"]), "{:.1f}% exit cap".format(p.get("exit_cap", 5.0)), "var(--text-primary)"),
        ("Projected Profit", fc(dp["profit"]), "{:.1f}% margin on cost".format(dp["profit_margin"]), pcol),
        ("Yield on Cost", "{:.2f}%".format(dp["return_on_cost"]), "{:+.2f}% spread to cap".format(spread),
         "var(--green)" if spread >= 1.0 else ("var(--amber)" if spread >= 0 else "var(--red)")),
    ]
    cells = ""
    for lbl, val, sub, vc in metrics:
        cells += (
            '<div style="flex:1;min-width:130px;padding:0.2rem 0.4rem;">'
            '<div style="font-size:0.62rem;font-weight:700;letter-spacing:0.6px;text-transform:uppercase;color:var(--text-muted);">{lbl}</div>'
            '<div style="font-size:1.45rem;font-weight:800;color:{vc};line-height:1.15;margin:0.15rem 0;">{val}</div>'
            '<div style="font-size:0.68rem;color:var(--text-tertiary);">{sub}</div>'
            '</div>'
        ).format(lbl=lbl, val=val, sub=sub, vc=vc)
    return (
        '<div class="card" style="padding:1.2rem 1.4rem;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.4rem;">'
        '<div style="font-size:0.7rem;font-weight:800;letter-spacing:1.2px;text-transform:uppercase;color:var(--text-muted);">Investment Summary</div>'
        '<div style="background:{bg};color:{col};border:1px solid {col};border-radius:999px;'
        'padding:0.28rem 0.8rem;font-size:0.72rem;font-weight:800;letter-spacing:0.5px;">{label}</div>'
        '</div>'
        '<div style="display:flex;flex-wrap:wrap;gap:0.6rem;margin:0.4rem 0 0.6rem;">{cells}</div>'
        '<div style="font-size:0.76rem;color:var(--text-secondary);line-height:1.5;border-top:1px solid var(--border);padding-top:0.6rem;">'
        '<b style="color:{col};">Recommendation:</b> {rationale}</div>'
        '</div>'
    ).format(bg=bg, col=col, label=label, cells=cells, rationale=rationale)


def _sources_uses_html(p, dp):
    """Sources & Uses table — the capital stack a lender/investor expects to see."""
    fc = format_currency
    total = dp["total_dev_cost"] or 1
    uses = [
        ("Land Acquisition", dp["land_price"]),
        ("Hard Costs (construction)", dp["hard_cost"]),
        ("Soft Costs (design, permits, fees)", dp["soft_cost"]),
        ("Parking", dp["parking_cost"]),
    ]
    use_rows = ""
    for lbl, amt in uses:
        use_rows += (
            '<tr><td style="padding:0.32rem 0;color:var(--text-secondary);font-size:0.8rem;">{lbl}</td>'
            '<td style="padding:0.32rem 0;text-align:right;color:var(--text-primary);font-weight:600;font-size:0.8rem;">{amt}</td>'
            '<td style="padding:0.32rem 0;text-align:right;color:var(--text-muted);font-size:0.72rem;width:54px;">{pct:.0f}%</td></tr>'
        ).format(lbl=lbl, amt=fc(amt), pct=amt / total * 100)
    src = [
        ("Senior Debt ({:.0f}% LTV)".format(p.get("ltv", 65)), dp["loan_amount"], "var(--accent)"),
        ("Sponsor / LP Equity", dp["equity"], "var(--gold)"),
    ]
    src_rows = ""
    for lbl, amt, c in src:
        src_rows += (
            '<tr><td style="padding:0.32rem 0;font-size:0.8rem;color:var(--text-secondary);">'
            '<span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:{c};margin-right:6px;"></span>{lbl}</td>'
            '<td style="padding:0.32rem 0;text-align:right;color:var(--text-primary);font-weight:600;font-size:0.8rem;">{amt}</td>'
            '<td style="padding:0.32rem 0;text-align:right;color:var(--text-muted);font-size:0.72rem;width:54px;">{pct:.0f}%</td></tr>'
        ).format(lbl=lbl, amt=fc(amt), pct=amt / total * 100, c=c)
    bar = (
        '<div style="display:flex;height:10px;border-radius:5px;overflow:hidden;margin:0.5rem 0 0.2rem;">'
        '<div style="width:{lw:.1f}%;background:var(--accent);"></div>'
        '<div style="width:{ew:.1f}%;background:var(--gold);"></div></div>'
    ).format(lw=dp["loan_amount"] / total * 100, ew=dp["equity"] / total * 100)
    return (
        '<div class="card" style="padding:1.1rem 1.3rem;">'
        '<div style="font-size:0.95rem;font-weight:800;color:var(--text-primary);margin-bottom:0.5rem;">Sources &amp; Uses</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.4rem;">'
        '<div><div style="font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-muted);margin-bottom:0.2rem;">Uses of Funds</div>'
        '<table style="width:100%;border-collapse:collapse;">{use_rows}'
        '<tr><td style="padding:0.4rem 0 0;border-top:1px solid var(--border);font-weight:800;font-size:0.82rem;color:var(--text-primary);">Total</td>'
        '<td style="padding:0.4rem 0 0;border-top:1px solid var(--border);text-align:right;font-weight:800;font-size:0.82rem;color:var(--text-primary);">{tot}</td><td style="border-top:1px solid var(--border);"></td></tr></table></div>'
        '<div><div style="font-size:0.66rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-muted);margin-bottom:0.2rem;">Sources of Capital</div>'
        '<table style="width:100%;border-collapse:collapse;">{src_rows}</table>{bar}'
        '<div style="font-size:0.7rem;color:var(--text-muted);margin-top:0.3rem;">'
        'Equity multiple at exit: <b style="color:var(--text-secondary);">{em:.2f}x</b> &middot; '
        'DSCR <b style="color:var(--text-secondary);">{dscr:.2f}x</b></div></div>'
        '</div></div>'
    ).format(
        use_rows=use_rows, src_rows=src_rows, bar=bar, tot=fc(dp["total_dev_cost"]),
        em=((dp["value_at_cap"] - dp["loan_amount"]) / dp["equity"]) if dp["equity"] else 0,
        dscr=dp["dscr"],
    )


def _scenarios_html(p):
    """Conservative / Base / Upside sensitivity — shows the deal under stress."""
    fc = format_currency
    base_inputs = {
        "lot_sf": p["lot_sf"], "far": p["far"], "max_height_ft": p["max_ht"],
        "max_floors": p["max_fl"], "floor_efficiency": p["floor_eff"] / 100.0,
        "rentable_efficiency": p["rent_eff"] / 100.0, "avg_unit_sf": p["avg_unit_sf"],
        "res_pct": p["res_pct"], "office_pct": p["office_pct"], "retail_pct": p["retail_pct"],
        "parking_ratio": p["parking_ratio"], "construction_psf": p["construction_psf"],
        "soft_cost_pct": p["soft_cost_pct"], "land_price": p["land_price"],
        "target_rent_res": p["target_rent_res"], "target_rent_office": p["target_rent_office"],
        "target_rent_retail": p["target_rent_retail"], "exit_cap": p["exit_cap"],
        "interest_rate": p["interest_rate"], "ltv": p["ltv"], "opex_ratio": 35,
    }
    sc = scenario_comparison(base_inputs)
    cols = [
        ("Conservative", sc["conservative"], "+15% costs, -10% rent, +75bps cap"),
        ("Base Case", sc["base"], "Your assumptions"),
        ("Upside", sc["upside"], "-8% costs, +10% rent, -50bps cap"),
    ]
    cards = ""
    for name, d, assume in cols:
        pcol = "var(--green)" if d["profit"] > 0 else "var(--red)"
        highlight = "border:1.5px solid var(--accent);" if name == "Base Case" else "border:1px solid var(--border);"
        cards += (
            '<div style="flex:1;min-width:150px;background:var(--bg-secondary);{hl}border-radius:10px;padding:0.8rem 0.9rem;">'
            '<div style="font-size:0.78rem;font-weight:800;color:var(--text-primary);">{name}</div>'
            '<div style="font-size:0.62rem;color:var(--text-muted);margin-bottom:0.5rem;min-height:1.6em;">{assume}</div>'
            '<div style="font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;">Profit</div>'
            '<div style="font-size:1.1rem;font-weight:800;color:{pcol};">{profit}</div>'
            '<div style="display:flex;justify-content:space-between;margin-top:0.4rem;font-size:0.72rem;">'
            '<span style="color:var(--text-tertiary);">Margin</span><span style="color:var(--text-secondary);font-weight:700;">{margin:.1f}%</span></div>'
            '<div style="display:flex;justify-content:space-between;font-size:0.72rem;">'
            '<span style="color:var(--text-tertiary);">Yield on cost</span><span style="color:var(--text-secondary);font-weight:700;">{roc:.2f}%</span></div>'
            '<div style="display:flex;justify-content:space-between;font-size:0.72rem;">'
            '<span style="color:var(--text-tertiary);">DSCR</span><span style="color:var(--text-secondary);font-weight:700;">{dscr:.2f}x</span></div>'
            '</div>'
        ).format(name=name, assume=assume, pcol=pcol, profit=fc(d["profit"]),
                 margin=d["profit_margin"], roc=d["return_on_cost"], dscr=d["dscr"], hl=highlight)
    return (
        '<div class="card" style="padding:1.1rem 1.3rem;">'
        '<div style="font-size:0.95rem;font-weight:800;color:var(--text-primary);margin-bottom:0.2rem;">Sensitivity &amp; Scenarios</div>'
        '<div style="font-size:0.76rem;color:var(--text-muted);margin-bottom:0.7rem;">'
        'How the deal holds up if costs, rents and cap rates move against (or for) us. A deal that still profits in the conservative column is a resilient deal.</div>'
        '<div style="display:flex;gap:0.7rem;flex-wrap:wrap;">{cards}</div>'
        '</div>'
    ).format(cards=cards)


def _disclaimer_html():
    return (
        '<div style="font-size:0.68rem;color:var(--text-muted);line-height:1.5;margin-top:0.4rem;padding:0.6rem 0.2rem;">'
        'This is a preliminary, high-level feasibility study generated from the inputs above and standard '
        'underwriting assumptions (5% vacancy, 35% operating-expense ratio, 30-year amortization). It is not an '
        'appraisal, offering, or investment advice. Actual results depend on entitlements, detailed design, '
        'construction bids, financing terms and market conditions at delivery.'
        '</div>'
    )


def _breakdown_html(p, dp):
    """Plain-English, client-facing explanation of how every number is derived."""
    fc = format_currency
    mo_rent = p.get("target_rent_res", 0)
    res_income = dp["est_units"] * mo_rent * 12
    cap = p.get("exit_cap", 5.0)
    far = p.get("far", 0)

    steps = ""
    # 1. Buildable area
    steps += _step_html(
        "1", "How much we can build",
        "{lot:,} sf lot &times; {far} FAR = {maxg:,} sf allowed &rarr; we build {gsf:,} sf over {fl} floors".format(
            lot=dp["lot_sf"], far=far, maxg=int(dp["max_gsf"]), gsf=dp["actual_gsf"], fl=dp["est_floors"]),
        "FAR (Floor Area Ratio) is the zoning multiplier that caps total floor area. Lot size &times; FAR = the maximum square footage the city lets us build on this parcel.",
    )
    # 2. Rentable + units
    steps += _step_html(
        "2", "Usable space &amp; apartments",
        "{gsf:,} sf &times; {eff}% efficiency = {rent:,} sf rentable &rarr; {units} apartments (&asymp;{avg:,} sf each)".format(
            gsf=dp["actual_gsf"], eff=p.get("rent_eff", 85), rent=dp["rentable_sf"],
            units=dp["est_units"], avg=dp["avg_unit_sf"]),
        "Not all built area can be rented &mdash; hallways, elevators, lobbies and walls take a share. The rentable portion is split into apartments based on the average unit size.",
    )
    # 3. Cost
    steps += _step_html(
        "3", "What it costs to build",
        "Hard {hc} + Soft {sc} + Parking {pc} + Land {ld} = {tot} all-in".format(
            hc=fc(dp["hard_cost"]), sc=fc(dp["soft_cost"]), pc=fc(dp["parking_cost"]),
            ld=fc(dp["land_price"]), tot=fc(dp["total_dev_cost"])),
        "Hard cost = construction (${psf}/sf). Soft cost = design, permits, fees &amp; financing. Plus parking and the land price. Together they are the total development cost.".format(
            psf=p.get("construction_psf", 0)),
    )
    # 4. Income -> NOI
    steps += _step_html(
        "4", "Yearly income &rarr; NOI",
        "Rent {gi}/yr &minus; 5% vacancy = {egi} &minus; {opp}% running costs = {noi} NOI".format(
            gi=fc(dp["gross_income"]), egi=fc(dp["egi"]), opp=35, noi=fc(dp["noi"])),
        "NOI (Net Operating Income) is the building&rsquo;s yearly profit from rent after vacancy and running costs (taxes, insurance, management, repairs) &mdash; but before any loan payment. It is THE number buyers use to value a building. Here {units} apartments at ${mo:,}/mo drive most of it.".format(
            units=dp["est_units"], mo=mo_rent),
    )
    # 5. Value & profit
    steps += _step_html(
        "5", "What the finished building is worth",
        "{noi} NOI &divide; {cap}% cap rate = {val} value &minus; {cost} cost = {profit} profit".format(
            noi=fc(dp["noi"]), cap=cap, val=fc(dp["value_at_cap"]),
            cost=fc(dp["total_dev_cost"]), profit=fc(dp["profit"])),
        "A cap rate is the yield buyers expect in this market. Dividing NOI by the cap rate gives the sale value (a {cap}% cap means buyers pay ~{mult:.0f}&times; the yearly NOI). Value minus what we spent = our profit. Return on cost = NOI &divide; cost = {roc:.1f}%.".format(
            cap=cap, mult=(100.0 / cap if cap else 0), roc=dp["return_on_cost"]),
    )
    # 6. Financing
    steps += _step_html(
        "6", "Financing &amp; safety check",
        "Loan {loan} ({ltv}% LTV) + Equity {eq} &middot; Debt service {ds}/yr &middot; DSCR {dscr:.2f}&times;".format(
            loan=fc(dp["loan_amount"]), ltv=p.get("ltv", 65), eq=fc(dp["equity"]),
            ds=fc(dp["annual_ds"]), dscr=dp["dscr"]),
        "The bank lends a share (LTV = loan-to-value); we fund the rest as equity. DSCR (Debt Service Coverage Ratio) checks safety: NOI &divide; loan payment. Above 1.25&times; is healthy &mdash; the rent comfortably covers the mortgage.",
    )

    return (
        '<div class="card" style="padding:1.1rem 1.3rem;margin-top:0.6rem;">'
        '<div style="font-size:0.95rem;font-weight:800;color:var(--text-primary);margin-bottom:0.2rem;">'
        'How we got to these numbers</div>'
        '<div style="font-size:0.76rem;color:var(--text-muted);margin-bottom:0.4rem;">'
        'A step-by-step walkthrough you can read with a client &mdash; no jargon left unexplained.</div>'
        '{steps}'
        '</div>'.format(steps=steps)
    )


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
            # 1. Executive summary + recommendation (what a principal reads first).
            st.markdown(_exec_summary_html(p, dp), unsafe_allow_html=True)
            # 2. Project facts table.
            st.markdown(rows, unsafe_allow_html=True)
            # 3. Capital stack.
            st.markdown(_sources_uses_html(p, dp), unsafe_allow_html=True)
            # 4. Downside/upside stress test.
            st.markdown(_scenarios_html(p), unsafe_allow_html=True)
            # 5. Plain-English walkthrough of how every number was derived.
            st.markdown(_breakdown_html(p, dp), unsafe_allow_html=True)
            # 6. Professional disclaimer.
            st.markdown(_disclaimer_html(), unsafe_allow_html=True)

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
