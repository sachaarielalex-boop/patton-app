from utils.property_data import format_currency

def sales_comparison_approach(comps, subject_sqft, subject_beds, subject_year, subject_lot):
    if not comps:
        return None
    valid = [c for c in comps if c.get("price") and c["price"] > 0 and c.get("sqft") and c["sqft"] > 0]
    if not valid:
        valid = [c for c in comps if c.get("price") and c["price"] > 0]
    if not valid:
        return None

    prices = [c["price"] for c in valid]
    psfs = [c["price"] / c["sqft"] for c in valid if c.get("sqft") and c["sqft"] > 0]

    result = {
        "count": len(valid),
        "median_price": sorted(prices)[len(prices) // 2],
        "avg_price": int(sum(prices) / len(prices)),
        "min_price": min(prices),
        "max_price": max(prices),
        "median_psf": sorted(psfs)[len(psfs) // 2] if psfs else None,
        "avg_psf": sum(psfs) / len(psfs) if psfs else None,
        "adjustments": [],
        "indicated_value": 0,
    }

    base_psf = result["median_psf"] or (result["median_price"] / max(subject_sqft, 800))

    adj = base_psf
    adjustments = []

    if subject_sqft and subject_sqft > 0:
        avg_sqft_comps = sum(c["sqft"] for c in valid if c.get("sqft") and c["sqft"] > 0)
        n_sqft = len([c for c in valid if c.get("sqft") and c["sqft"] > 0])
        if n_sqft:
            avg_sqft_comps = avg_sqft_comps / n_sqft
            size_diff_pct = (subject_sqft - avg_sqft_comps) / avg_sqft_comps * 100
            if abs(size_diff_pct) > 5:
                size_adj = -size_diff_pct * 0.15
                adj += adj * size_adj / 100
                direction = "smaller" if size_diff_pct < 0 else "larger"
                adjustments.append({
                    "factor": "Size Adjustment",
                    "detail": "Subject is {:.0f}% {} than avg comp ({:,.0f} vs {:,.0f} sqft)".format(
                        abs(size_diff_pct), direction, subject_sqft, avg_sqft_comps),
                    "impact_pct": size_adj,
                    "impact_dollar": adj * size_adj / 100 * max(subject_sqft, 800),
                    "direction": "up" if size_adj > 0 else "down",
                })

    if subject_year and subject_year > 1900:
        avg_year_comps = []
        for c in valid:
            yr = c.get("year_built", "")
            if yr and str(yr).isdigit() and int(yr) > 1900:
                avg_year_comps.append(int(yr))
        if avg_year_comps:
            avg_yr = sum(avg_year_comps) / len(avg_year_comps)
            age_diff = subject_year - avg_yr
            if abs(age_diff) > 3:
                age_adj = age_diff * 0.5
                adj += adj * age_adj / 100
                direction = "newer" if age_diff > 0 else "older"
                adjustments.append({
                    "factor": "Age/Condition",
                    "detail": "Subject is {:.0f} years {} than avg comp (built {} vs {:.0f})".format(
                        abs(age_diff), direction, subject_year, avg_yr),
                    "impact_pct": age_adj,
                    "impact_dollar": adj * age_adj / 100 * max(subject_sqft, 800),
                    "direction": "up" if age_adj > 0 else "down",
                })

    if subject_lot and subject_lot > 0:
        avg_lot_comps = []
        for c in valid:
            ls = c.get("lot_sf")
            if ls and ls > 0:
                avg_lot_comps.append(ls)
        if avg_lot_comps:
            avg_lt = sum(avg_lot_comps) / len(avg_lot_comps)
            lot_diff_pct = (subject_lot - avg_lt) / avg_lt * 100
            if abs(lot_diff_pct) > 10:
                lot_adj = lot_diff_pct * 0.10
                adj += adj * lot_adj / 100
                direction = "smaller" if lot_diff_pct < 0 else "larger"
                adjustments.append({
                    "factor": "Lot Size",
                    "detail": "Subject lot is {:.0f}% {} ({:,.0f} vs {:,.0f} sqft)".format(
                        abs(lot_diff_pct), direction, subject_lot, avg_lt),
                    "impact_pct": lot_adj,
                    "impact_dollar": adj * lot_adj / 100 * max(subject_sqft, 800),
                    "direction": "up" if lot_adj > 0 else "down",
                })

    indicated = int(adj * max(subject_sqft, 800))
    result["adjusted_psf"] = adj
    result["indicated_value"] = indicated
    result["adjustments"] = adjustments
    return result


def income_approach(noi, market_cap, alt_caps=None):
    if not noi or not market_cap or market_cap <= 0:
        return None
    value = noi / (market_cap / 100)
    result = {
        "noi": noi,
        "cap_rate": market_cap,
        "indicated_value": int(value),
        "scenarios": [],
    }
    caps = alt_caps or [market_cap - 1, market_cap - 0.5, market_cap, market_cap + 0.5, market_cap + 1]
    for c in caps:
        if c > 0:
            result["scenarios"].append({"cap": c, "value": int(noi / (c / 100))})
    return result


def cost_approach(lot_sf, land_psf, building_sf, construction_psf, year_built, current_year=2026):
    if not lot_sf or not building_sf:
        return None
    land_value = lot_sf * (land_psf or 80)
    replacement = building_sf * (construction_psf or 200)
    age = max(current_year - (year_built or 2000), 0)
    dep_rate = min(age * 1.5, 70)
    depreciation = replacement * dep_rate / 100
    indicated = int(land_value + replacement - depreciation)
    return {
        "land_sf": lot_sf,
        "land_psf": land_psf or 80,
        "land_value": int(land_value),
        "building_sf": building_sf,
        "construction_psf": construction_psf or 200,
        "replacement_cost": int(replacement),
        "age": age,
        "depreciation_pct": dep_rate,
        "depreciation": int(depreciation),
        "indicated_value": indicated,
    }


def reconcile(sales_val, income_val, cost_val, property_type="residential"):
    values = {}
    if sales_val and sales_val.get("indicated_value"):
        values["Sales Comparison"] = sales_val["indicated_value"]
    if income_val and income_val.get("indicated_value"):
        values["Income"] = income_val["indicated_value"]
    if cost_val and cost_val.get("indicated_value"):
        values["Cost"] = cost_val["indicated_value"]
    if not values:
        return None

    if property_type in ["investment", "multifamily", "commercial"]:
        weights = {"Sales Comparison": 0.30, "Income": 0.50, "Cost": 0.20}
    elif property_type in ["land", "vacant"]:
        weights = {"Sales Comparison": 0.60, "Income": 0.05, "Cost": 0.35}
    else:
        weights = {"Sales Comparison": 0.50, "Income": 0.30, "Cost": 0.20}

    weighted_sum = 0
    total_weight = 0
    breakdown = []
    for approach, val in values.items():
        w = weights.get(approach, 0.33)
        weighted_sum += val * w
        total_weight += w
        breakdown.append({"approach": approach, "value": val, "weight": w})

    reconciled = int(weighted_sum / total_weight) if total_weight else 0
    return {
        "reconciled_value": reconciled,
        "breakdown": breakdown,
        "property_type": property_type,
    }


def value_drivers_html(nb, parcel, geo, comps_count=0):
    drivers = []

    if nb:
        mkt = nb.get("mkt", {})
        yoy = mkt.get("yoy", 0)
        if yoy > 6:
            drivers.append({"factor": "Market Momentum", "impact": "Strong positive",
                "why": "{}% YoY appreciation signals strong demand exceeding supply. Buyers are competing, pushing values up.".format(yoy),
                "color": "var(--green)"})
        elif yoy > 3:
            drivers.append({"factor": "Market Momentum", "impact": "Moderate positive",
                "why": "{}% YoY appreciation is above inflation, indicating healthy organic demand growth.".format(yoy),
                "color": "var(--blue)"})
        else:
            drivers.append({"factor": "Market Momentum", "impact": "Flat/Weak",
                "why": "{}% YoY appreciation barely keeps pace with inflation. Market is price-sensitive.".format(yoy),
                "color": "var(--amber)"})

        dom = mkt.get("dom", 99)
        if dom < 25:
            drivers.append({"factor": "Speed of Sale", "impact": "Very fast market",
                "why": "{} days on market means properties move quickly. Sellers have leverage. Low inventory drives urgency.".format(dom),
                "color": "var(--green)"})
        elif dom < 45:
            drivers.append({"factor": "Speed of Sale", "impact": "Balanced market",
                "why": "{} days on market is healthy. Neither buyers nor sellers dominate. Fair pricing matters.".format(dom),
                "color": "var(--blue)"})
        else:
            drivers.append({"factor": "Speed of Sale", "impact": "Slow market",
                "why": "{} days on market suggests oversupply or overpricing. Buyers have negotiating power.".format(dom),
                "color": "var(--amber)"})

        inv = mkt.get("inv_mo", 6)
        if inv < 3:
            drivers.append({"factor": "Supply/Demand", "impact": "Seller's market",
                "why": "{} months of inventory (under 3 = seller's market). Limited choices force buyers to pay asking or above.".format(inv),
                "color": "var(--green)"})
        elif inv < 6:
            drivers.append({"factor": "Supply/Demand", "impact": "Balanced",
                "why": "{} months of inventory. Market is equilibrium — neither constrained nor oversupplied.".format(inv),
                "color": "var(--blue)"})
        else:
            drivers.append({"factor": "Supply/Demand", "impact": "Buyer's market",
                "why": "{} months of inventory (over 6 = buyer's market). Excess supply compresses pricing power.".format(inv),
                "color": "var(--amber)"})

        pipeline = mkt.get("units_pipeline", 0)
        absorption = mkt.get("absorption", 50)
        if pipeline > 0:
            if absorption > 80:
                drivers.append({"factor": "New Supply Pipeline", "impact": "{:,} units absorbing well".format(pipeline),
                    "why": "{}% absorption rate means new units are being absorbed. Pipeline adds competition but demand keeps pace.".format(absorption),
                    "color": "var(--blue)"})
            else:
                drivers.append({"factor": "New Supply Pipeline", "impact": "{:,} units — absorption risk".format(pipeline),
                    "why": "{}% absorption with {:,} units in pipeline creates downward pricing pressure. Excess supply discounts values.".format(absorption, pipeline),
                    "color": "var(--amber)"})

        scores = nb.get("scores", {})
        walk = scores.get("walk", 0)
        if walk >= 80:
            drivers.append({"factor": "Walkability", "impact": "Premium location",
                "why": "Walk Score {} is 'Very Walkable'. Walkable neighborhoods command 10-20% premiums over car-dependent areas.".format(walk),
                "color": "var(--green)"})
        elif walk >= 60:
            drivers.append({"factor": "Walkability", "impact": "Somewhat walkable",
                "why": "Walk Score {} is moderate. Some errands can be done on foot. Marginal walkability premium.".format(walk),
                "color": "var(--blue)"})

        if nb.get("oz"):
            drivers.append({"factor": "Opportunity Zone", "impact": "Tax incentive premium",
                "why": "OZ designation attracts capital gains investors who accept lower current yields for tax deferral. This increases buyer pool and supports higher valuations.",
                "color": "var(--green)"})

        flood = nb.get("flood", "")
        if "VE" in flood:
            drivers.append({"factor": "Flood Risk", "impact": "Significant discount",
                "why": "VE flood zone = high-velocity coastal flooding. Insurance costs $8,000-$15,000+/yr, directly reducing NOI and suppressing values.",
                "color": "var(--red)"})
        elif "AE" in flood:
            drivers.append({"factor": "Flood Risk", "impact": "Moderate discount",
                "why": "AE flood zone requires flood insurance ($2,000-$6,000/yr). Adds carrying cost that buyers factor into offers.",
                "color": "var(--amber)"})
        elif "X" in flood:
            drivers.append({"factor": "Flood Risk", "impact": "Minimal — Zone X",
                "why": "Zone X = minimal flood risk. No mandatory flood insurance. This is a positive for valuations vs. coastal areas.",
                "color": "var(--green)"})

        demo = nb.get("demo", {})
        income = demo.get("income", 0)
        if income > 60000:
            drivers.append({"factor": "Area Income", "impact": "High purchasing power",
                "why": "Median income ${:,} supports higher rents and sale prices. Buyer/renter pool can afford premium pricing.".format(income),
                "color": "var(--green)"})
        elif income < 35000:
            drivers.append({"factor": "Area Income", "impact": "Constrained purchasing power",
                "why": "Median income ${:,} limits rent ceilings and buyer pool depth. Values are capped by what residents can afford.".format(income),
                "color": "var(--amber)"})

    if parcel:
        yr = parcel.get("YEAR BUILT")
        if yr and str(yr).isdigit() and int(yr) > 1900:
            age = 2026 - int(yr)
            if age > 40:
                drivers.append({"factor": "Building Age", "impact": "Significant depreciation",
                    "why": "Built {} ({} years old). Older structures face higher maintenance, code compliance costs, and buyer resistance. Functional obsolescence discounts 1-2% per year.".format(yr, age),
                    "color": "var(--amber)"})
            elif age < 10:
                drivers.append({"factor": "Building Age", "impact": "Near-new premium",
                    "why": "Built {} ({} years old). Modern construction commands premium — current code, warranties active, no deferred maintenance.".format(yr, age),
                    "color": "var(--green)"})

    html = '<div class="card"><div class="card-title">Why the Market Values It This Way</div>'
    for d in drivers:
        html += '<div style="padding:0.7rem 0;border-bottom:1px solid var(--slate-100);">'
        html += '<div style="display:flex;justify-content:space-between;align-items:center;">'
        html += '<span style="font-size:0.82rem;font-weight:600;color:var(--navy);">{}</span>'.format(d["factor"])
        html += '<span style="font-size:0.7rem;font-weight:600;color:{};">{}</span>'.format(d["color"], d["impact"])
        html += '</div>'
        html += '<p style="font-size:0.78rem;color:var(--slate-500);line-height:1.6;margin:0.3rem 0 0;">{}</p>'.format(d["why"])
        html += '</div>'
    if not drivers:
        html += '<div class="alert-info">Not enough data to identify value drivers.</div>'
    html += '</div>'
    return html
