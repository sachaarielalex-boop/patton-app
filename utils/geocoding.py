import streamlit as st
import requests

GEO_URL = "https://nominatim.openstreetmap.org/search"
REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

@st.cache_data(ttl=3600, show_spinner=False)
def geocode(addr):
    result = {"lat": None, "lon": None, "display": "", "city": "", "county": "", "state": "",
              "zip": "", "confidence": 0, "source": "Nominatim/OSM"}
    try:
        r = requests.get(GEO_URL, params={
            "q": f"{addr}, Miami, FL", "format": "json", "limit": 1, "addressdetails": 1
        }, headers={"User-Agent": "PATTON/2.0"}, timeout=10)
        d = r.json()
        if d:
            result["lat"] = float(d[0]["lat"])
            result["lon"] = float(d[0]["lon"])
            result["display"] = d[0].get("display_name", addr)
            ad = d[0].get("address", {})
            result["city"] = ad.get("city", ad.get("town", ad.get("village", "")))
            result["county"] = ad.get("county", "Miami-Dade County")
            result["state"] = ad.get("state", "Florida")
            result["zip"] = ad.get("postcode", "")
            imp = float(d[0].get("importance", 0))
            result["confidence"] = min(int(imp * 100), 100) if imp else 60
    except Exception:
        pass
    return result

@st.cache_data(ttl=3600, show_spinner=False)
def reverse_geocode(lat, lon):
    """Resolve a clicked map point to a street address (best-effort)."""
    try:
        r = requests.get(REVERSE_URL, params={
            "lat": lat, "lon": lon, "format": "json", "addressdetails": 1, "zoom": 18
        }, headers={"User-Agent": "PATTON/2.0"}, timeout=10)
        d = r.json()
        ad = d.get("address", {})
        house = ad.get("house_number", "")
        road = ad.get("road", "")
        city = ad.get("city", ad.get("town", ad.get("village", "Miami")))
        street = (house + " " + road).strip() if road else ""
        if street:
            return (street + ", " + city + ", FL").strip(", ")
        return d.get("display_name", "{:.5f}, {:.5f}".format(lat, lon))
    except Exception:
        return "{:.5f}, {:.5f}".format(lat, lon)


MIAMI_DADE_URL = "https://opendata.miamidade.gov/resource/k9zy-wfpd.json"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_property_records(addr):
    try:
        clean = addr.split(",")[0].strip()
        r = requests.get(MIAMI_DADE_URL, params={
            "$where": f"upper(site_addr) like upper('%{clean}%')", "$limit": 15
        }, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_pois(lat, lon):
    pois = {}
    cats = {
        "Dining": '[amenity~"restaurant|bar|cafe"]',
        "Education": '[amenity~"school|university|college"]',
        "Healthcare": '[amenity~"hospital|clinic|pharmacy"]',
        "Shopping": '[shop~"supermarket|convenience|mall|department_store"]',
        "Parks": '[leisure~"park|playground|garden|fitness_centre"]',
        "Transit": '[public_transport~"station|stop_position"]',
        "Banks": '[amenity~"bank|atm"]',
    }
    for name, tag in cats.items():
        try:
            q = f"[out:json][timeout:8];node{tag}(around:2500,{lat},{lon});out body 8;"
            r = requests.post("https://overpass-api.de/api/interpreter", data={"data": q}, timeout=10)
            if r.status_code == 200:
                pois[name] = [{"name": e.get("tags", {}).get("name", "Unnamed"), "lat": e["lat"], "lon": e["lon"]}
                              for e in r.json().get("elements", []) if "lat" in e and e.get("tags", {}).get("name")]
        except Exception:
            pois[name] = []
    return pois

SAMPLE_ADDRESSES = [
    "858 W Flagler St, Miami, FL",
    "2121 NW 22nd Ct, Miami, FL",
    "1300 Brickell Bay Dr, Miami, FL",
    "2700 NW 2nd Ave, Miami, FL",
    "3531 Main Hwy, Miami, FL",
]
