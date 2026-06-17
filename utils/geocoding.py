import streamlit as st
import requests
import math

GEO_URL = "https://nominatim.openstreetmap.org/search"
REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"


def _census_geocode(addr):
    """Geocode a US address via the free US Census Bureau API.

    Unlike Nominatim it is not IP-rate-limited, so it works reliably on Streamlit
    Cloud. US-only (fine for Miami-Dade). Returns a geo dict or None.
    """
    one_line = addr if "," in addr else "{}, Miami, FL".format(addr)
    try:
        r = requests.get(CENSUS_URL, params={
            "address": one_line, "benchmark": "Public_AR_Current", "format": "json",
        }, headers={"User-Agent": "PATTON/2.0"}, timeout=15)
        matches = r.json().get("result", {}).get("addressMatches", [])
        if not matches:
            return None
        m = matches[0]
        coords = m.get("coordinates", {})
        comp = m.get("addressComponents", {})
        return {
            "lat": float(coords["y"]),
            "lon": float(coords["x"]),
            "display": m.get("matchedAddress", addr),
            "city": comp.get("city", "").title() or "Miami",
            "county": "Miami-Dade County",
            "state": comp.get("state", "FL"),
            "zip": comp.get("zip", ""),
            "confidence": 90,
            "source": "US Census",
        }
    except Exception:
        return None


def _local_lookup(addr):
    """Resolve an address against the bundled 1,776-parcel database.

    Streamlit Cloud's shared IPs are frequently rate-limited/blocked by Nominatim,
    so the local parcel database (which already carries Latitude/Longitude) is the
    most reliable source. Returns a geo dict or None.
    """
    try:
        from parcels_data import ADDR_DATA
    except Exception:
        return None
    clean = (addr or "").upper().split(",")[0].strip()
    if not clean:
        return None
    parcel = ADDR_DATA.get(clean)
    if parcel is None:
        for k, v in ADDR_DATA.items():
            if clean in k or k in clean:
                parcel = v
                break
    if parcel is None:
        return None
    try:
        lat = float(parcel.get("Latitude"))
        lon = float(parcel.get("Longitude"))
    except (TypeError, ValueError):
        return None
    return {
        "lat": lat, "lon": lon,
        "display": parcel.get("Address", addr),
        "city": parcel.get("City", "Miami"),
        "county": "Miami-Dade County",
        "state": parcel.get("State", "Florida"),
        "zip": "",
        "confidence": 95,
        "source": "Parcel database",
    }


@st.cache_data(ttl=3600, show_spinner=False)
def geocode(addr):
    # Local parcel database first (instant, reliable on Streamlit Cloud).
    local = _local_lookup(addr)
    if local:
        return local

    # US Census next (free, no key, not IP-blocked on Cloud).
    census = _census_geocode(addr)
    if census:
        return census

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


def _nearest_parcel(lat, lon):
    """Return (address, distance_miles) of the closest parcel, or (None, None)."""
    try:
        from parcels_data import ADDR_DATA
    except Exception:
        return None, None
    best_addr, best_d = None, None
    for v in ADDR_DATA.values():
        try:
            plat = float(v.get("Latitude"))
            plon = float(v.get("Longitude"))
        except (TypeError, ValueError):
            continue
        dlat = math.radians(plat - lat)
        dlon = math.radians(plon - lon)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(lat)) * math.cos(math.radians(plat)) * math.sin(dlon / 2) ** 2)
        d = 3959 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        if best_d is None or d < best_d:
            best_d = d
            city = v.get("City", "Miami")
            state = v.get("State", "FL")
            addr = v.get("Address", "")
            best_addr = "{}, {}, {}".format(addr, city, state) if addr else None
    return best_addr, best_d


@st.cache_data(ttl=3600, show_spinner=False)
def reverse_geocode(lat, lon):
    """Resolve a clicked map point to a street address (best-effort).

    Tries the nearest known parcel first (works offline / on Cloud), then Nominatim,
    and only falls back to raw coordinates if nothing resolves.
    """
    # Nearest parcel within ~0.3 mi is treated as a confident match.
    addr, dist = _nearest_parcel(lat, lon)
    if addr and dist is not None and dist <= 0.3:
        return addr

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
        disp = d.get("display_name", "")
        if disp:
            return disp
    except Exception:
        pass

    # Fall back to the nearest parcel even if a little further out.
    if addr:
        return addr
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
