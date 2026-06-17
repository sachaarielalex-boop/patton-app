import streamlit as st
import folium
from streamlit_folium import st_folium
import pydeck as pdk
import math
import os

COMP_COLORS = {
    "subject": "#0f172a",
    "sale": "#2563eb",
    "rent": "#16a34a",
    "dev": "#7c3aed",
    "risk": "#dc2626",
    "default": "#64748b",
}

FOLIUM_COLORS = {
    "subject": "black",
    "sale": "blue",
    "rent": "green",
    "dev": "purple",
    "risk": "red",
    "default": "gray",
}

LEGEND_HTML = """
<div style="position:fixed;bottom:30px;left:50px;z-index:1000;background:white;
padding:10px 14px;border-radius:8px;border:1px solid #e2e8f0;font-size:12px;
font-family:Inter,sans-serif;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
<div style="font-weight:700;margin-bottom:6px;color:#0f172a;">Map Legend</div>
{rows}
</div>
"""


def _legend_row(color, label):
    return '<div style="display:flex;align-items:center;gap:6px;margin:3px 0;"><span style="width:10px;height:10px;border-radius:50%;background:{};display:inline-block;"></span><span style="color:#475569;">{}</span></div>'.format(color, label)


def _distance_mi(lat1, lon1, lat2, lon2):
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 3959 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def render_map_2d(lat, lon, label="Property", comps=None, radius_miles=1, show_legend=True, zoom=16):
    # OpenStreetMap tiles show street names and building footprints clearly, which
    # makes it much easier to read the area and pick the right spot.
    mp = folium.Map(location=[lat, lon], zoom_start=zoom, tiles="OpenStreetMap", control_scale=True)

    folium.Marker(
        [lat, lon],
        popup=folium.Popup("<b style='font-size:13px;'>{}</b><br><span style='background:#0f172a;color:white;padding:2px 6px;border-radius:3px;font-size:10px;'>SUBJECT</span>".format(label), max_width=280),
        tooltip=label,
        icon=folium.Icon(color="black", icon="home", prefix="fa"),
    ).add_to(mp)

    for r, c, n in [(0.5, "#94a3b8", "0.5 mi"), (1, "#64748b", "1 mi"), (3, "#475569", "3 mi")]:
        if r <= radius_miles:
            folium.Circle([lat, lon], radius=int(r * 1609), color=c, weight=1.5,
                          fill=True, fill_opacity=0.015, dash_array="5,5").add_to(mp)

    legend_items = [_legend_row("#0f172a", "Subject Property")]

    if comps:
        has_types = set()
        for s in comps:
            comp_type = s.get("comp_type", "sale")
            has_types.add(comp_type)
            clr = COMP_COLORS.get(comp_type, COMP_COLORS["default"])
            fclr = FOLIUM_COLORS.get(comp_type, "gray")
            dist = _distance_mi(lat, lon, s["lat"], s["lon"])

            popup_parts = ["<b style='font-size:12px;'>{}</b>".format(s.get("addr", "Unknown"))]
            if s.get("price"):
                popup_parts.append("<span style='font-size:12px;font-weight:600;color:#0f172a;'>${:,}</span>".format(s["price"]))
            if s.get("type"):
                popup_parts.append("<span style='color:#64748b;font-size:11px;'>{}</span>".format(s["type"]))
            popup_parts.append("<span style='color:#94a3b8;font-size:10px;'>{:.2f} mi from subject</span>".format(dist))
            if s.get("source"):
                popup_parts.append("<span style='background:#f1f5f9;color:#475569;padding:1px 5px;border-radius:3px;font-size:9px;'>{}</span>".format(s["source"]))
            popup_html = "<br>".join(popup_parts)

            icon_name = "building" if comp_type == "dev" else ("dollar-sign" if comp_type == "sale" else ("key" if comp_type == "rent" else "exclamation-triangle"))

            folium.CircleMarker(
                [s["lat"], s["lon"]], radius=7, color=clr, fill=True,
                fill_color=clr, fill_opacity=0.75, weight=2,
                popup=folium.Popup(popup_html, max_width=250),
            ).add_to(mp)

        type_labels = {"sale": "Sale Comps", "rent": "Rental Comps", "dev": "Development", "risk": "Risk / Underperforming"}
        for t in ["sale", "rent", "dev", "risk"]:
            if t in has_types:
                legend_items.append(_legend_row(COMP_COLORS[t], type_labels[t]))

    if show_legend and len(legend_items) > 1:
        legend = LEGEND_HTML.format(rows="".join(legend_items))
        mp.get_root().html.add_child(folium.Element(legend))

    return mp


def render_map_2d_widget(lat, lon, **kwargs):
    mp = render_map_2d(lat, lon, **kwargs)
    st_folium(mp, width=None, height=500, returned_objects=[])


def render_map_3d(lat, lon, label="Property", comps=None, color_mode="type"):
    subject_data = [{"lat": lat, "lon": lon, "height": 40, "color": [15, 23, 42, 220], "name": label, "is_subject": True}]
    comp_data = []
    if comps:
        color_map = {
            "sale": [37, 99, 235, 180],
            "rent": [22, 163, 74, 180],
            "dev": [124, 58, 237, 180],
            "risk": [220, 38, 38, 180],
        }
        for c in comps:
            if c.get("lat") and c.get("lon"):
                ct = c.get("comp_type", "sale")
                h = min(max(c.get("price", 300000) / 30000, 8), 60) if color_mode == "value" else 20
                clr = color_map.get(ct, [100, 116, 139, 180])
                comp_data.append({
                    "lat": c["lat"], "lon": c["lon"],
                    "height": h, "color": clr,
                    "name": c.get("addr", ""), "is_subject": False,
                })

    all_data = subject_data + comp_data

    subject_layer = pdk.Layer(
        "ColumnLayer",
        data=subject_data,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=50,
        get_fill_color="color",
        radius=25,
        pickable=True,
    )

    layers = [subject_layer]
    if comp_data:
        comp_layer = pdk.Layer(
            "ColumnLayer",
            data=comp_data,
            get_position=["lon", "lat"],
            get_elevation="height",
            elevation_scale=30,
            get_fill_color="color",
            radius=18,
            pickable=True,
        )
        layers.append(comp_layer)

    ring_points = []
    for r_miles in [0.25, 0.5, 1.0]:
        for angle in range(0, 360, 4):
            rad = math.radians(angle)
            dlat = (r_miles / 69.0) * math.cos(rad)
            dlon = (r_miles / (69.0 * math.cos(math.radians(lat)))) * math.sin(rad)
            ring_points.append({"lat": lat + dlat, "lon": lon + dlon})

    ring_layer = pdk.Layer(
        "ScatterplotLayer",
        data=ring_points,
        get_position=["lon", "lat"],
        get_radius=12,
        get_fill_color=[100, 116, 139, 50],
    )
    layers.append(ring_layer)

    view = pdk.ViewState(latitude=lat, longitude=lon, zoom=15, pitch=55, bearing=-15)
    style = "mapbox://styles/mapbox/light-v11" if os.getenv("MAPBOX_API_KEY", "") else "light"
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style=style,
        tooltip={"text": "{name}"},
    )
    st.pydeck_chart(deck)


def map_links(lat, lon, addr=""):
    clean = addr.replace(" ", "+") if addr else "{},{}".format(lat, lon)
    return {
        "Google Maps": "https://www.google.com/maps/search/?api=1&query={},{}".format(lat, lon),
        "Street View": "https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={},{}".format(lat, lon),
        "Google Earth": "https://earth.google.com/web/@{},{},50a,500d,35y,0h,0t,0r".format(lat, lon),
        "FEMA Flood Map": "https://msc.fema.gov/portal/search?AddressQuery={}".format(clean),
    }
