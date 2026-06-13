import json
import csv
import io
import datetime

from utils.property_data import format_currency, format_number


def export_json(data, addr):
    payload = {
        "report": "PATTON Investment Report",
        "address": addr,
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data": data,
    }
    return json.dumps(payload, indent=2, default=str)


def export_csv(data, addr):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["PATTON Investment Report", addr, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
    w.writerow([])
    if isinstance(data, dict):
        for section, content in data.items():
            w.writerow(["--- {} ---".format(section)])
            if isinstance(content, dict):
                for k, v in content.items():
                    w.writerow([k, v])
            elif isinstance(content, list):
                header_done = False
                for item in content:
                    if isinstance(item, dict):
                        if not header_done:
                            w.writerow(list(item.keys()))
                            header_done = True
                        w.writerow(list(item.values()))
                    else:
                        w.writerow([item])
            else:
                w.writerow([content])
            w.writerow([])
    return buf.getvalue()


def build_report_data(geo, nb_name, nb, records, parcel):
    report = {}
    report["Location"] = {
        "Address": geo.get("display", "N/A"),
        "City": geo.get("city", "N/A"),
        "County": geo.get("county", "Miami-Dade"),
        "State": geo.get("state", "Florida"),
        "ZIP": geo.get("zip", "N/A"),
        "Coordinates": "{}, {}".format(geo.get("lat", "N/A"), geo.get("lon", "N/A")),
        "Neighborhood": nb_name or "N/A",
    }
    if parcel:
        report["Property"] = {
            "Folio": parcel.get("FOLIO #", "N/A"),
            "Owner": parcel.get("true_owner1", "N/A"),
            "Land Use": parcel.get("LAND USE", "N/A"),
            "Lot Size": "{} sqft".format(format_number(parcel.get("LOT SIZE"))),
            "Building Area": "{} sqft".format(format_number(parcel.get("BUILDING AREA"))),
            "Year Built": parcel.get("YEAR BUILT", "N/A"),
            "Zoning": parcel.get("ZONING CODE", "N/A"),
            "Last Sale": format_currency(parcel.get("SALE PRICE")),
            "Sale Date": parcel.get("SALE DATE", "N/A"),
        }
    if nb:
        mkt = nb.get("mkt", {})
        report["Market"] = {
            "Median Price": format_currency(mkt.get("med_price")),
            "Price/sqft": "${}".format(mkt.get("psf", 0)),
            "Avg Rent": "{}/mo".format(format_currency(mkt.get("rent"))),
            "Gross Yield": "{}%".format(mkt.get("yield", 0)),
            "YoY Appreciation": "+{}%".format(mkt.get("yoy", 0)),
            "Days on Market": str(mkt.get("dom", "N/A")),
            "Inventory": "{} months".format(mkt.get("inv_mo", "N/A")),
        }
        report["Highlights"] = nb.get("highlights", [])
        report["Risks"] = nb.get("risks", [])
    return report


def export_professional_html(addr, geo, nb_name, nb, parcel, scores, financials, recommendation, dev_plan, val_rec):
    now = datetime.datetime.now().strftime("%B %d, %Y")
    overall = scores.get("overall", 0) if scores else 0
    mkt = nb.get("mkt", {}) if nb else {}
    demo = nb.get("demo", {}) if nb else {}

    def _sec(title):
        return '<div class="rpt-sec"><h2>{}</h2></div>'.format(title)

    def _trow(k, v, bold=False):
        w = "font-weight:700;" if bold else ""
        return '<tr><td style="padding:6px 10px;border-bottom:1px solid #e2e8f0;color:#475569;font-size:13px;">{}</td><td style="padding:6px 10px;border-bottom:1px solid #e2e8f0;color:#0f172a;font-weight:600;font-size:13px;text-align:right;{}">{}</td></tr>'.format(k, w, v)

    def _table(rows_html):
        return '<table style="width:100%;border-collapse:collapse;margin:10px 0;">{}</table>'.format(rows_html)

    def _card(title, content):
        return '<div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px 20px;margin:12px 0;background:white;"><div style="font-size:14px;font-weight:700;color:#0f172a;border-bottom:1px solid #e2e8f0;padding-bottom:8px;margin-bottom:10px;">{}</div>{}</div>'.format(title, content)

    def _badge(text, color):
        return '<span style="display:inline-block;background:{bg};color:{fg};padding:4px 12px;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;">{text}</span>'.format(
            bg=color + "18", fg=color, text=text)

    def _metric(label, value, sub=""):
        s = '<div style="font-size:11px;color:#94a3b8;margin-top:2px;">{}</div>'.format(sub) if sub else ""
        return '<div style="text-align:center;padding:12px;"><div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">{}</div><div style="font-size:22px;font-weight:800;color:#0f172a;margin:4px 0;">{}</div>{}</div>'.format(label, value, s)

    html = []
    html.append('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">')
    html.append('<title>PATTON Report - {}</title>'.format(addr))
    html.append('<style>')
    html.append("@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');")
    html.append('*{margin:0;padding:0;box-sizing:border-box;}')
    html.append('body{font-family:Inter,-apple-system,sans-serif;color:#0f172a;line-height:1.6;background:#f8fafc;}')
    html.append('.rpt-page{max-width:850px;margin:0 auto;padding:40px;}')
    html.append('.rpt-cover{text-align:center;padding:80px 40px;border:1px solid #e2e8f0;border-radius:12px;background:white;margin-bottom:30px;}')
    html.append('.rpt-cover h1{font-size:32px;font-weight:800;color:#0f172a;letter-spacing:-0.5px;margin-bottom:8px;}')
    html.append('.rpt-cover .addr{font-size:18px;color:#2563eb;font-weight:600;margin:12px 0;}')
    html.append('.rpt-cover .meta{font-size:12px;color:#64748b;margin-top:16px;}')
    html.append('.rpt-sec h2{font-size:16px;font-weight:700;color:#0f172a;border-bottom:2px solid #2563eb;display:inline-block;padding-bottom:4px;margin:28px 0 14px;}')
    html.append('.metrics-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin:12px 0;}')
    html.append('.metric-box{border:1px solid #e2e8f0;border-radius:8px;background:white;padding:12px;text-align:center;}')
    html.append('.metric-box .ml{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;}')
    html.append('.metric-box .mv{font-size:20px;font-weight:700;color:#0f172a;margin:4px 0;}')
    html.append('.metric-box .ms{font-size:11px;color:#94a3b8;}')
    html.append('.disclaimer{font-size:10px;color:#94a3b8;text-align:center;margin-top:40px;padding-top:20px;border-top:1px solid #e2e8f0;}')
    html.append('@media print{body{background:white;}.rpt-page{padding:20px;}}')
    html.append('</style></head><body><div class="rpt-page">')

    # Cover
    html.append('<div class="rpt-cover">')
    html.append('<div style="font-size:11px;color:#94a3b8;letter-spacing:3px;text-transform:uppercase;margin-bottom:20px;">INVESTMENT ANALYSIS REPORT</div>')
    html.append('<h1>PATTON</h1>')
    html.append('<div style="width:40px;height:3px;background:#2563eb;margin:12px auto;border-radius:2px;"></div>')
    html.append('<div class="addr">{}</div>'.format(addr))
    if nb_name:
        html.append('<div style="font-size:13px;color:#475569;">{} Submarket | Miami-Dade County, FL</div>'.format(nb_name))
    html.append('<div class="meta">')
    html.append('Report Date: {} &nbsp;|&nbsp; '.format(now))
    html.append('Data Confidence: {}% &nbsp;|&nbsp; '.format(scores.get("data_confidence", 0) if scores else 0))
    html.append('Investment Score: {}/100'.format(overall))
    html.append('</div>')
    if recommendation:
        html.append('<div style="margin-top:20px;">{}</div>'.format(_badge(recommendation["verdict"], recommendation["verdict_color"])))
    html.append('</div>')

    # Executive Summary
    html.append(_sec("1. Executive Summary"))
    if recommendation:
        html.append(_card("Investment Verdict", '<div style="text-align:center;padding:8px;">'
            '<div style="font-size:24px;font-weight:800;color:{};">{}</div>'
            '<div style="font-size:13px;color:#64748b;margin-top:4px;">Highest & Best Use: {}</div>'
            '<div style="font-size:13px;color:#64748b;">Strategy: {}</div>'
            '</div>'.format(recommendation["verdict_color"], recommendation["verdict"], recommendation["hbu"], recommendation["strategy"])))

    metric_boxes = ""
    metric_boxes += '<div class="metric-box"><div class="ml">Score</div><div class="mv">{}/100</div></div>'.format(overall)
    if financials:
        metric_boxes += '<div class="metric-box"><div class="ml">NOI</div><div class="mv">{}</div></div>'.format(format_currency(financials.get("noi", 0)))
        metric_boxes += '<div class="metric-box"><div class="ml">Cap Rate</div><div class="mv">{:.1f}%</div></div>'.format(financials.get("cap_rate", 0))
        metric_boxes += '<div class="metric-box"><div class="ml">CoC Return</div><div class="mv">{:.1f}%</div></div>'.format(financials.get("coc", 0))
        metric_boxes += '<div class="metric-box"><div class="ml">DSCR</div><div class="mv">{:.2f}x</div></div>'.format(financials.get("dscr", 0))
    if mkt.get("yoy"):
        metric_boxes += '<div class="metric-box"><div class="ml">YoY Growth</div><div class="mv">+{}%</div></div>'.format(mkt["yoy"])
    html.append('<div class="metrics-row">{}</div>'.format(metric_boxes))

    # Property Overview
    html.append(_sec("2. Property Overview"))
    rows = _trow("Address", geo.get("display", addr))
    rows += _trow("Submarket", nb_name or "N/A")
    if parcel:
        rows += _trow("Property Type", parcel.get("LAND USE", "N/A"))
        rows += _trow("Lot Size", "{} sqft".format(format_number(parcel.get("LOT SIZE"))))
        rows += _trow("Building Area", "{} sqft".format(format_number(parcel.get("BUILDING AREA"))))
        rows += _trow("Year Built", str(parcel.get("YEAR BUILT", "N/A")))
        rows += _trow("Owner", parcel.get("true_owner1", "N/A"))
        rows += _trow("Folio #", parcel.get("FOLIO #", "N/A"))
        rows += _trow("Last Sale Price", format_currency(parcel.get("SALE PRICE")))
        rows += _trow("Sale Date", str(parcel.get("SALE DATE", "N/A")))
        rows += _trow("Zoning", parcel.get("ZONING CODE", "N/A"))
    else:
        rows += _trow("Coordinates", "{}, {}".format(geo.get("lat", "N/A"), geo.get("lon", "N/A")))
    html.append(_card("Property Details", _table(rows)))

    # Zoning
    if nb and nb.get("zoning"):
        html.append(_sec("3. Zoning & Development"))
        z = nb["zoning"]
        rows = _trow("Zone Code", z.get("primary", "N/A"))
        rows += _trow("Max FAR", str(z.get("max_far", "N/A")))
        rows += _trow("Max Height", z.get("max_height", "N/A"))
        rows += _trow("Permitted Uses", z.get("allowed_uses", "N/A"))
        rows += _trow("Parking", z.get("parking", "N/A"))
        if z.get("setbacks"):
            rows += _trow("Setbacks", z["setbacks"])
        html.append(_card("Zoning Details", _table(rows)))

    if dev_plan:
        rows = _trow("Lot Size", "{:,} sqft".format(dev_plan.get("lot_sf", 0)))
        rows += _trow("Max Buildable GSF", "{:,} sqft".format(dev_plan.get("max_gsf", 0)))
        rows += _trow("Actual GSF", "{:,} sqft".format(dev_plan.get("actual_gsf", 0)))
        rows += _trow("Rentable SF", "{:,} sqft".format(dev_plan.get("rentable_sf", 0)))
        rows += _trow("Estimated Units", str(dev_plan.get("est_units", 0)))
        rows += _trow("Floors", str(dev_plan.get("est_floors", 0)))
        rows += _trow("Total Dev Cost", format_currency(dev_plan.get("total_dev_cost", 0)))
        rows += _trow("Value at Cap", format_currency(dev_plan.get("value_at_cap", 0)))
        rows += _trow("Profit", format_currency(dev_plan.get("profit", 0)), bold=True)
        rows += _trow("Return on Cost", "{:.1f}%".format(dev_plan.get("return_on_cost", 0)))
        html.append(_card("Development Feasibility", _table(rows)))

    # Market
    if nb:
        html.append(_sec("4. Market Analysis"))
        rows = _trow("Median Price", format_currency(mkt.get("med_price")))
        rows += _trow("Price/SF", "${}".format(mkt.get("psf", "N/A")))
        rows += _trow("Avg Rent", "{}/mo".format(format_currency(mkt.get("rent"))))
        rows += _trow("Gross Yield", "{}%".format(mkt.get("yield", "N/A")))
        rows += _trow("YoY Growth", "+{}%".format(mkt.get("yoy", "N/A")))
        rows += _trow("Days on Market", str(mkt.get("dom", "N/A")))
        rows += _trow("Inventory", "{} months".format(mkt.get("inv_mo", "N/A")))
        rows += _trow("Absorption", "{}%".format(mkt.get("absorption", "N/A")))
        rows += _trow("List/Sale Ratio", "{}%".format(mkt.get("ls_ratio", "N/A")))
        html.append(_card("Submarket Indicators", _table(rows)))

        rows = _trow("Population", "{:,}".format(demo.get("pop", 0)))
        rows += _trow("Median Income", format_currency(demo.get("income")))
        rows += _trow("Median Age", str(demo.get("age", "N/A")))
        rows += _trow("Owner-Occupied", "{}%".format(demo.get("owner", "N/A")))
        rows += _trow("Vacancy Rate", "{}%".format(demo.get("vacancy", "N/A")))
        html.append(_card("Demographics", _table(rows)))

    # Financial
    if financials:
        html.append(_sec("5. Financial Analysis"))
        rows = _trow("Gross Rent", format_currency(financials.get("gross_rent", 0)))
        rows += _trow("Less Vacancy", "-{}".format(format_currency(financials.get("vacancy_loss", 0))))
        rows += _trow("Effective Gross Income", format_currency(financials.get("egi", 0)))
        rows += _trow("Total OpEx", "-{}".format(format_currency(financials.get("opex", 0))))
        rows += _trow("Net Operating Income", format_currency(financials.get("noi", 0)), bold=True)
        rows += _trow("Debt Service", "-{}".format(format_currency(financials.get("debt_service", 0))))
        rows += _trow("Annual Cash Flow", format_currency(financials.get("cash_flow", 0)), bold=True)
        html.append(_card("Income & Cash Flow", _table(rows)))

        rows = _trow("Cap Rate", "{:.1f}%".format(financials.get("cap_rate", 0)))
        rows += _trow("Cash-on-Cash", "{:.1f}%".format(financials.get("coc", 0)))
        rows += _trow("DSCR", "{:.2f}x".format(financials.get("dscr", 0)))
        rows += _trow("GRM", "{:.1f}x".format(financials.get("grm", 0)))
        rows += _trow("Breakeven Occupancy", "{:.0f}%".format(financials.get("breakeven", 0)))
        html.append(_card("Return Metrics", _table(rows)))

    # Valuation
    if val_rec:
        html.append(_sec("6. Valuation"))
        html.append('<div style="text-align:center;padding:16px;border:1px solid #e2e8f0;border-radius:8px;background:white;margin:12px 0;">'
            '<div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Reconciled Value</div>'
            '<div style="font-size:28px;font-weight:800;color:#0f172a;margin:6px 0;">{}</div>'
            '<div style="font-size:12px;color:#94a3b8;">Weighted by {} property type</div>'
            '</div>'.format(format_currency(val_rec.get("reconciled_value", 0)), val_rec.get("property_type", "residential")))
        rows = ""
        for b in val_rec.get("breakdown", []):
            rows += _trow("{} ({}%)".format(b["approach"], int(b["weight"] * 100)), format_currency(b["value"]))
        if rows:
            html.append(_card("Approach Breakdown", _table(rows)))

    # Risk
    html.append(_sec("7. Risk Analysis"))
    if nb:
        rows = ""
        rows += _trow("Flood Zone", nb.get("flood", "N/A"))
        rows += _trow("Crime Index", "{}/100".format(nb.get("crime", "N/A")))
        rows += _trow("School Rating", str(nb.get("school", "N/A")))
        rows += _trow("Opportunity Zone", "Yes" if nb.get("oz") else "No")
        html.append(_card("Risk Factors", _table(rows)))
    if scores:
        rows = ""
        for label, key in [("Location", "location"), ("Market", "market"), ("Financial", "financial"), ("Risk", "risk"), ("Data Confidence", "data_confidence"), ("Overall", "overall")]:
            bold = key == "overall"
            rows += _trow(label, "{}/100".format(scores.get(key, 0)), bold=bold)
        html.append(_card("Score Breakdown", _table(rows)))

    # Recommendation
    if recommendation:
        html.append(_sec("8. Best Recommendation"))
        html.append('<div style="text-align:center;padding:16px;border:2px solid {};border-radius:10px;background:white;margin:12px 0;">'
            '<div style="font-size:22px;font-weight:800;color:{};">{}</div>'
            '<div style="font-size:13px;color:#64748b;margin-top:6px;">Strategy: {} | HBU: {}</div>'
            '</div>'.format(recommendation["verdict_color"], recommendation["verdict_color"], recommendation["verdict"], recommendation["strategy"], recommendation["hbu"]))

        html.append(_card("Investment Memo", '<p style="font-size:13px;color:#475569;line-height:1.7;">{}</p>'.format(recommendation["memo"])))

        reasons_html = '<ol style="font-size:13px;color:#475569;line-height:1.8;padding-left:20px;">'
        for title, detail in recommendation.get("reasons", [])[:5]:
            reasons_html += '<li><b>{}</b> &mdash; {}</li>'.format(title, detail)
        reasons_html += '</ol>'
        html.append(_card("Top Reasons For", reasons_html))

        flags_html = '<ol style="font-size:13px;color:#475569;line-height:1.8;padding-left:20px;">'
        for title, detail in recommendation.get("red_flags", [])[:5]:
            flags_html += '<li><b style="color:#dc2626;">{}</b> &mdash; {}</li>'.format(title, detail)
        flags_html += '</ol>'
        html.append(_card("Red Flags", flags_html))

        html.append(_card("What I Would Do as the Investor",
            '<p style="font-size:13px;color:#0f172a;line-height:1.7;font-style:italic;">&ldquo;{}&rdquo;</p>'.format(recommendation["investor_take"])))

    # Disclaimer
    html.append('<div class="disclaimer">')
    html.append('<p><b>DISCLAIMER:</b> This report is for preliminary analysis only and is not a formal appraisal. '
        'Data may include estimated, demo, or unverified sources. All financial projections are hypothetical. '
        'Consult licensed professionals before making investment decisions.</p>')
    html.append('<p style="margin-top:8px;">Generated by PATTON | Patton Commercial Real Estate Intelligence | {}</p>'.format(now))
    html.append('</div>')

    html.append('</div></body></html>')
    return "\n".join(html)


def export_markdown(data, addr, scores=None, financials=None, nb_name=None):
    lines = []
    lines.append("# PATTON Investment Report")
    lines.append("**Address:** {}".format(addr))
    lines.append("**Generated:** {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    lines.append("**Neighborhood:** {}".format(nb_name or "N/A"))
    lines.append("")
    if scores:
        lines.append("## Investment Score")
        lines.append("| Category | Score |")
        lines.append("|----------|-------|")
        for label, key in [("Location", "location"), ("Market", "market"), ("Financial", "financial"), ("Risk", "risk"), ("Data Confidence", "data_confidence"), ("**Overall**", "overall")]:
            lines.append("| {} | {}/100 |".format(label, scores.get(key, "N/A")))
        lines.append("")
    if financials:
        lines.append("## Financial Analysis")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append("| NOI | {} |".format(format_currency(financials.get("noi", 0))))
        lines.append("| Cap Rate | {:.1f}% |".format(financials.get("cap_rate", 0)))
        lines.append("| Cash-on-Cash | {:.1f}% |".format(financials.get("coc", 0)))
        lines.append("| DSCR | {:.2f}x |".format(financials.get("dscr", 0)))
        lines.append("| Monthly Cash Flow | {} |".format(format_currency(financials.get("cash_flow", 0) / 12)))
        lines.append("")
    if isinstance(data, dict):
        for section, content in data.items():
            lines.append("## {}".format(section))
            if isinstance(content, dict):
                lines.append("| Field | Value |")
                lines.append("|-------|-------|")
                for k, v in content.items():
                    lines.append("| {} | {} |".format(k, v))
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        lines.append("- " + ", ".join("{}: {}".format(k, v) for k, v in item.items()))
                    else:
                        lines.append("- {}".format(item))
            else:
                lines.append(str(content))
            lines.append("")
    lines.append("---")
    lines.append("*Generated by PATTON - Patton Commercial Real Estate Intelligence*")
    lines.append("")
    lines.append("*DISCLAIMER: This report is for preliminary analysis only and is not a formal appraisal.*")
    return "\n".join(lines)
