MIAMI21_ZONES = {
    "T3-R": {"name": "Sub-Urban", "max_height": "35 ft (3 stories)", "max_far": 1.0, "density": "9 du/acre", "use": "Single-family, duplex, townhouse", "parking": "2/unit", "color": "#16a34a"},
    "T3-L": {"name": "Sub-Urban Limited", "max_height": "35 ft (3 stories)", "max_far": 0.75, "density": "9 du/acre", "use": "Single-family", "parking": "2/unit", "color": "#22c55e"},
    "T4-R": {"name": "General Urban", "max_height": "45 ft (4 stories)", "max_far": 2.0, "density": "36 du/acre", "use": "Multi-family, townhouse, mixed-use", "parking": "1.5/unit", "color": "#eab308"},
    "T4-L": {"name": "General Urban Limited", "max_height": "45 ft (4 stories)", "max_far": 1.5, "density": "18 du/acre", "use": "Multi-family, limited retail", "parking": "1.5/unit", "color": "#facc15"},
    "T5-O": {"name": "Urban Center Open", "max_height": "65 ft (5 stories)", "max_far": 3.5, "density": "65 du/acre", "use": "Mixed-use, retail, office, residential", "parking": "1/unit", "color": "#f97316"},
    "T5-L": {"name": "Urban Center Limited", "max_height": "56 ft (5 stories)", "max_far": 2.5, "density": "36 du/acre", "use": "Mixed-use, limited commercial", "parking": "1/unit", "color": "#fb923c"},
    "T6-O": {"name": "Urban Core Open", "max_height": "75 ft (8 stories)", "max_far": 5.0, "density": "150 du/acre", "use": "Mixed-use, high-density residential, hotel", "parking": "0.5/unit", "color": "#ef4444"},
    "T6-8": {"name": "Urban Core 8", "max_height": "85 ft (8 stories)", "max_far": 4.5, "density": "150 du/acre", "use": "High-density mixed-use", "parking": "0.75/unit", "color": "#dc2626"},
    "T6-12": {"name": "Urban Core 12", "max_height": "128 ft (12 stories)", "max_far": 7.5, "density": "150 du/acre", "use": "High-density mixed-use", "parking": "0.75/unit", "color": "#b91c1c"},
    "T6-24": {"name": "Urban Core 24", "max_height": "250 ft (24 stories)", "max_far": 12.0, "density": "300 du/acre", "use": "High-rise mixed-use, waterfront", "parking": "1/unit", "color": "#991b1b"},
    "T6-36": {"name": "Urban Core 36", "max_height": "375 ft (36 stories)", "max_far": 18.0, "density": "500 du/acre", "use": "Towers, office, hotel, luxury condo", "parking": "1.5/unit", "color": "#7f1d1d"},
    "T6-48": {"name": "Urban Core 48", "max_height": "500 ft (48 stories)", "max_far": 20.0, "density": "500 du/acre", "use": "Supertall towers, CBD", "parking": "1.5/unit", "color": "#581c87"},
    "T6-80": {"name": "Urban Core 80", "max_height": "850 ft (80 stories)", "max_far": 25.0, "density": "1000 du/acre", "use": "Supertall, unlimited density", "parking": "1.5/unit", "color": "#4c1d95"},
    "EU-S": {"name": "Estate Single-Family", "max_height": "35 ft", "max_far": 0.5, "density": "6 du/acre", "use": "Single-family residential", "parking": "2/unit", "color": "#a3e635"},
    "EU-M": {"name": "Estate Multi-Family", "max_height": "35 ft", "max_far": 0.75, "density": "12 du/acre", "use": "Single/multi-family", "parking": "2/unit", "color": "#84cc16"},
    "NRD-1": {"name": "Neighborhood Revitalization District", "max_height": "Varies", "max_far": "Varies", "density": "Varies", "use": "Wynwood Art District overlay", "parking": "0.75/unit", "color": "#8b5cf6"},
    # Coral Gables Zoning (separate from Miami 21)
    "MX-2": {"name": "Mixed-Use 2 (Coral Gables)", "max_height": "190 ft (varies)", "max_far": 4.5, "density": "N/A (commercial)", "use": "Office, Retail, Restaurant, Hotel, Mixed-Use, Professional Services", "parking": "3.3/1,000 RSF", "color": "#6366f1"},
    "MX-1": {"name": "Mixed-Use 1 (Coral Gables)", "max_height": "97 ft", "max_far": 2.5, "density": "N/A (commercial)", "use": "Office, Retail, Restaurant, Mixed-Use", "parking": "3.3/1,000 RSF", "color": "#818cf8"},
    "C": {"name": "Commercial (Coral Gables)", "max_height": "150 ft (varies)", "max_far": 3.5, "density": "N/A (commercial)", "use": "Office, Retail, Restaurant, Professional Services, Medical", "parking": "3.3/1,000 RSF", "color": "#a78bfa"},
}

def get_zone_info(code):
    if not code:
        return None
    clean = code.strip().upper().replace("_", "-")
    for k, v in MIAMI21_ZONES.items():
        if k.upper() in clean:
            return dict(v, code=k)
    return None

def estimate_buildable(lot_sf, far, efficiency=0.85):
    if not lot_sf or not far:
        return {}
    gfa = lot_sf * far
    nra = gfa * efficiency
    avg_unit = 850
    est_units = int(nra / avg_unit)
    return {
        "lot_sf": lot_sf,
        "far": far,
        "gross_floor_area": int(gfa),
        "net_rentable": int(nra),
        "est_units": max(est_units, 1),
        "efficiency": efficiency,
    }

def zoning_summary_html(zone_data, nb_zoning=None):
    if not zone_data and not nb_zoning:
        return '<div class="alert-warn">Zoning data unavailable for this address.</div>'
    z = zone_data or {}
    nz = nb_zoning or {}
    rows = []
    rows.append(_row("Zone Code", z.get("code", nz.get("primary", "N/A"))))
    rows.append(_row("Zone Name", z.get("name", "N/A")))
    rows.append(_row("Max Height", z.get("max_height", nz.get("max_height", "N/A"))))
    rows.append(_row("Max FAR", z.get("max_far", nz.get("max_far", "N/A"))))
    rows.append(_row("Density", z.get("density", "N/A")))
    rows.append(_row("Permitted Uses", z.get("use", nz.get("allowed_uses", "N/A"))))
    rows.append(_row("Parking Req.", z.get("parking", nz.get("parking", "N/A"))))
    if nz.get("setbacks"):
        rows.append(_row("Setbacks", nz["setbacks"]))
    if nz.get("min_lot"):
        rows.append(_row("Min Lot Size", nz["min_lot"]))
    return '<table class="dtable">' + "".join(rows) + '</table>'

def _row(k, v):
    return '<tr><td class="dk">{}</td><td class="dv">{}</td></tr>'.format(k, v)
