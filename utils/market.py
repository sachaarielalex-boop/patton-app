def get_competition(neighborhood):
    try:
        from data import COMPETITION
    except ImportError:
        return []
    return COMPETITION.get(neighborhood, [])

def get_land_comps(neighborhood):
    try:
        from data import LAND_COMPS
    except ImportError:
        return []
    return LAND_COMPS.get(neighborhood, [])

def get_dev_recommendation(neighborhood):
    try:
        from data import DEV_RECOMMENDATIONS
    except ImportError:
        return None
    return DEV_RECOMMENDATIONS.get(neighborhood, None)

def market_summary_html(mkt, demo):
    if not mkt:
        return '<div class="alert-warn">Market data unavailable.</div>'
    rows = []
    rows.append(_r("Median Price", _cur(mkt.get("med_price"))))
    rows.append(_r("Price / sqft", _cur(mkt.get("psf"))))
    rows.append(_r("Price Range", mkt.get("range", "N/A")))
    rows.append(_r("Avg Rent", _cur(mkt.get("rent")) + "/mo"))
    rows.append(_r("Gross Yield", "{}%".format(mkt.get("yield", "N/A"))))
    rows.append(_r("YoY Appreciation", "+{}%".format(mkt.get("yoy", "N/A"))))
    rows.append(_r("Days on Market", str(mkt.get("dom", "N/A"))))
    rows.append(_r("Inventory (months)", str(mkt.get("inv_mo", "N/A"))))
    rows.append(_r("List/Sale Ratio", "{}%".format(mkt.get("ls_ratio", "N/A"))))
    rows.append(_r("Absorption Rate", "{}%".format(mkt.get("absorption", "N/A"))))
    rows.append(_r("Units in Pipeline", "{:,}".format(mkt.get("units_pipeline", 0))))
    return '<table class="dtable">' + "".join(rows) + '</table>'

def demo_summary_html(demo):
    if not demo:
        return '<div class="alert-warn">Demographic data unavailable.</div>'
    rows = []
    rows.append(_r("Population", "{:,}".format(demo.get("pop", 0))))
    rows.append(_r("Median Income", _cur(demo.get("income"))))
    rows.append(_r("Median Age", str(demo.get("age", "N/A"))))
    rows.append(_r("Owner-Occupied", "{}%".format(demo.get("owner", "N/A"))))
    rows.append(_r("Renter-Occupied", "{}%".format(demo.get("renter", "N/A"))))
    rows.append(_r("Vacancy Rate", "{}%".format(demo.get("vacancy", "N/A"))))
    rows.append(_r("College Educated", "{}%".format(demo.get("college", "N/A"))))
    rows.append(_r("Foreign-Born", "{}%".format(demo.get("foreign", "N/A"))))
    return '<table class="dtable">' + "".join(rows) + '</table>'

def comp_table_html(comps):
    if not comps:
        return '<div class="alert-info">No competition data available for this area.</div>'
    html = '<table class="dtable"><tr style="border-bottom:2px solid var(--slate-300);">'
    html += '<td class="dk" style="font-weight:700;">Project</td>'
    html += '<td class="dk" style="font-weight:700;">Developer</td>'
    html += '<td class="dk" style="font-weight:700;">Units</td>'
    html += '<td class="dk" style="font-weight:700;">Type</td>'
    html += '<td class="dk" style="font-weight:700;">Status</td>'
    html += '<td class="dk" style="font-weight:700;">PSF</td></tr>'
    for c in comps:
        psf = ""
        if c.get("psf_sale"):
            psf = "${}/sf (sale)".format(c["psf_sale"])
        elif c.get("psf_rent"):
            psf = "${:.2f}/sf (rent)".format(c["psf_rent"])
        html += '<tr>'
        html += '<td class="dv">{}</td>'.format(c.get("name", ""))
        html += '<td class="dk">{}</td>'.format(c.get("dev", ""))
        html += '<td class="dv">{}</td>'.format(c.get("units", ""))
        html += '<td class="dk">{}</td>'.format(c.get("type", ""))
        html += '<td class="dk">{}</td>'.format(c.get("status", ""))
        html += '<td class="dv">{}</td>'.format(psf)
        html += '</tr>'
    return html + '</table>'

def land_comp_table_html(comps):
    if not comps:
        return '<div class="alert-info">No land comp data available for this area.</div>'
    html = '<table class="dtable"><tr style="border-bottom:2px solid var(--slate-300);">'
    html += '<td class="dk" style="font-weight:700;">Address</td>'
    html += '<td class="dk" style="font-weight:700;">Lot SF</td>'
    html += '<td class="dk" style="font-weight:700;">Price</td>'
    html += '<td class="dk" style="font-weight:700;">$/SF</td>'
    html += '<td class="dk" style="font-weight:700;">Zoning</td>'
    html += '<td class="dk" style="font-weight:700;">Date</td></tr>'
    for c in comps:
        html += '<tr>'
        html += '<td class="dv">{}</td>'.format(c.get("addr", ""))
        html += '<td class="dv">{:,}</td>'.format(c.get("lot_sf", 0))
        html += '<td class="dv">${:,}</td>'.format(c.get("sale_price", 0))
        html += '<td class="dv">${}</td>'.format(c.get("psf_land", 0))
        html += '<td class="dk">{}</td>'.format(c.get("zoning", ""))
        html += '<td class="dk">{}</td>'.format(c.get("date", ""))
        html += '</tr>'
    return html + '</table>'

def _r(k, v):
    return '<tr><td class="dk">{}</td><td class="dv">{}</td></tr>'.format(k, v)

def _cur(v):
    if v is None:
        return "N/A"
    try:
        v = float(str(v).replace(",", ""))
    except (ValueError, TypeError):
        return "N/A"
    if v >= 1_000_000:
        return "${:,.1f}M".format(v / 1_000_000)
    return "${:,.0f}".format(v)
