import streamlit as st
import requests
import csv
import io

REDFIN_CSV = "https://www.redfin.com/stingray/api/gis-csv"
REDFIN_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

NB_BOUNDS = {
    "Allapattah": {"poly": "-80.26 25.79,-80.22 25.79,-80.22 25.83,-80.26 25.83,-80.26 25.79", "zip": "33142"},
    "Coconut Grove": {"poly": "-80.26 25.71,-80.23 25.71,-80.23 25.74,-80.26 25.74,-80.26 25.71", "zip": "33133"},
    "Westchester": {"poly": "-80.37 25.72,-80.33 25.72,-80.33 25.76,-80.37 25.76,-80.37 25.72", "zip": "33165"},
    "Little Havana": {"poly": "-80.24 25.76,-80.21 25.76,-80.21 25.78,-80.24 25.78,-80.24 25.76", "zip": "33135"},
    "Wynwood": {"poly": "-80.21 25.79,-80.19 25.79,-80.19 25.81,-80.21 25.81,-80.21 25.79", "zip": "33127"},
    "Brickell": {"poly": "-80.20 25.75,-80.18 25.75,-80.18 25.77,-80.20 25.77,-80.20 25.75", "zip": "33131"},
    "Overtown": {"poly": "-80.21 25.78,-80.19 25.78,-80.19 25.80,-80.21 25.80,-80.21 25.78", "zip": "33136"},
    "Edgewater": {"poly": "-80.20 25.78,-80.18 25.78,-80.18 25.81,-80.20 25.81,-80.20 25.78", "zip": "33137"},
    "Coral Gables": {"poly": "-80.28 25.72,-80.24 25.72,-80.24 25.76,-80.28 25.76,-80.28 25.72", "zip": "33134"},
    "Downtown Miami": {"poly": "-80.20 25.77,-80.18 25.77,-80.18 25.79,-80.20 25.79,-80.20 25.77", "zip": "33132"},
}

def _lat_lon_poly(lat, lon, radius_deg=0.015):
    w = lon - radius_deg
    e = lon + radius_deg
    s = lat - radius_deg
    n = lat + radius_deg
    return "{w} {s},{e} {s},{e} {n},{w} {n},{w} {s}".format(w=w, e=e, s=s, n=n)

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_redfin_active(poly, max_results=200):
    try:
        r = requests.get(REDFIN_CSV, params={
            "al": 1, "market": "miami",
            "num_homes": max_results,
            "sf": "1,2,3,5,6,7",
            "status": 9,
            "uipt": "1,2,3,4,5,6",
            "v": 8,
            "poly": poly,
        }, headers=REDFIN_HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        return _parse_redfin(r.text)
    except Exception:
        return []

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_redfin_sold(poly, days=365, max_results=200):
    try:
        r = requests.get(REDFIN_CSV, params={
            "al": 1, "market": "miami",
            "num_homes": max_results,
            "sf": "1,2,3,5,6,7",
            "sold_within_days": days,
            "status": 9,
            "uipt": "1,2,3,4,5,6",
            "v": 8,
            "poly": poly,
        }, headers=REDFIN_HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        return _parse_redfin(r.text)
    except Exception:
        return []

def _parse_redfin(text):
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        addr = (row.get("ADDRESS") or "").strip()
        if not addr:
            sale_type = (row.get("SALE TYPE") or "").lower()
            if "accordance" in sale_type or not sale_type:
                continue
        if "accordance" in addr.lower():
            continue
        price_str = (row.get("PRICE") or "").replace(",", "").strip()
        price = int(float(price_str)) if price_str and price_str.replace(".", "").isdigit() else 0
        sqft_str = (row.get("SQUARE FEET") or "").replace(",", "").strip()
        sqft = int(float(sqft_str)) if sqft_str and sqft_str.replace(".", "").isdigit() else 0
        lot_str = (row.get("LOT SIZE") or "").replace(",", "").strip()
        lot = int(float(lot_str)) if lot_str and lot_str.replace(".", "").isdigit() else 0
        beds_str = (row.get("BEDS") or "").strip()
        beds = int(float(beds_str)) if beds_str and beds_str.replace(".", "").isdigit() else None
        baths_str = (row.get("BATHS") or "").strip()
        baths = float(baths_str) if baths_str and baths_str.replace(".", "").isdigit() else None
        dom_str = (row.get("DAYS ON MARKET") or "").strip()
        dom = int(dom_str) if dom_str and dom_str.isdigit() else None
        psf_str = (row.get("$/SQUARE FEET") or "").replace(",", "").strip()
        psf = float(psf_str) if psf_str and psf_str.replace(".", "").isdigit() else None
        hoa_str = (row.get("HOA/MONTH") or "").replace(",", "").strip()
        hoa = int(float(hoa_str)) if hoa_str and hoa_str.replace(".", "").isdigit() else None
        url_key = [k for k in row.keys() if "URL" in k]
        url = (row.get(url_key[0]) or "") if url_key else ""
        lat_str = (row.get("LATITUDE") or "").strip()
        lon_str = (row.get("LONGITUDE") or "").strip()

        rows.append({
            "address": addr,
            "city": row.get("CITY") or "",
            "zip": row.get("ZIP OR POSTAL CODE") or "",
            "price": price,
            "beds": beds,
            "baths": baths,
            "sqft": sqft,
            "lot_sf": lot,
            "psf": psf,
            "year_built": row.get("YEAR BUILT") or "",
            "dom": dom,
            "hoa": hoa,
            "status": row.get("STATUS") or "",
            "type": row.get("PROPERTY TYPE") or "",
            "sold_date": row.get("SOLD DATE") or "",
            "url": url,
            "lat": float(lat_str) if lat_str else None,
            "lon": float(lon_str) if lon_str else None,
            "source": "Redfin",
            "mls": row.get("MLS#") or "",
        })
    return rows

def fetch_comps_for_neighborhood(nb_name, status="active"):
    bounds = NB_BOUNDS.get(nb_name)
    if not bounds:
        return []
    poly = bounds["poly"]
    if status == "sold":
        return fetch_redfin_sold(poly, days=365, max_results=200)
    return fetch_redfin_active(poly, max_results=200)

def fetch_comps_around(lat, lon, radius_mi=1, status="active"):
    deg = radius_mi * 0.0145
    poly = _lat_lon_poly(lat, lon, deg)
    if status == "sold":
        return fetch_redfin_sold(poly, days=365, max_results=200)
    return fetch_redfin_active(poly, max_results=200)

def external_search_links(addr, lat, lon, nb_name=None, zipcode=None):
    clean = addr.replace(" ", "+") if addr else ""
    z = zipcode or "33130"
    links = {}
    links["Zillow"] = "https://www.zillow.com/homes/{}_rb/".format(clean)
    links["Redfin"] = "https://www.redfin.com/zipcode/{}/filter/sort=lo-days".format(z)
    links["Realtor.com"] = "https://www.realtor.com/realestateandhomes-search/{}_Miami_FL".format(z)
    links["Apartments.com"] = "https://www.apartments.com/miami-fl-{}/".format(z)
    links["CondoBlackBook"] = "https://www.condoblackbook.com/miami-condos-for-sale"
    links["LoopNet"] = "https://www.loopnet.com/search/commercial-real-estate/miami-fl-{}/for-sale/".format(z)
    links["Trulia"] = "https://www.trulia.com/FL/Miami/{}/".format(z)
    links["Compass"] = "https://www.compass.com/homes-for-sale/miami-fl/filterby=price/"
    if nb_name:
        nb_slug = nb_name.lower().replace(" ", "-")
        links["Zillow"] = "https://www.zillow.com/{}-miami-fl/".format(nb_slug)
        links["Redfin"] = "https://www.redfin.com/neighborhood/274718/FL/Miami/{}".format(nb_slug.title().replace("-", "-"))
    return links

def rental_search_links(nb_name=None, zipcode=None):
    z = zipcode or "33130"
    links = {}
    links["Zillow Rentals"] = "https://www.zillow.com/homes/for_rent/{}_rb/".format(z)
    links["Apartments.com"] = "https://www.apartments.com/miami-fl-{}/".format(z)
    links["Rent.com"] = "https://www.rent.com/florida/miami-apartments?zip={}".format(z)
    links["HotPads"] = "https://hotpads.com/miami-fl-{}/apartments-for-rent".format(z)
    links["Rentometer"] = "https://www.rentometer.com/analysis/new?location=Miami+FL+{}&beds=2".format(z)
    return links
