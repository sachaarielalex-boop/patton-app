from utils.property_data import format_currency


def generate_recommendation(geo, nb_name, nb, parcel, scores, financials, val_rec, comps_count=0):
    overall = scores.get("overall", 0) if scores else 0
    loc = scores.get("location", 0) if scores else 0
    mkt_sc = scores.get("market", 0) if scores else 0
    fin_sc = scores.get("financial", 0) if scores else 0
    risk_sc = scores.get("risk", 0) if scores else 0
    data_sc = scores.get("data_confidence", 0) if scores else 0

    mkt = nb.get("mkt", {}) if nb else {}
    demo = nb.get("demo", {}) if nb else {}

    if data_sc < 35:
        verdict = "Needs More Data"
        verdict_color = "#d97706"
    elif overall >= 72:
        verdict = "Strong Opportunity"
        verdict_color = "#16a34a"
    elif overall >= 55:
        verdict = "Watch"
        verdict_color = "#2563eb"
    elif overall >= 40:
        verdict = "Proceed with Caution"
        verdict_color = "#d97706"
    else:
        verdict = "Avoid"
        verdict_color = "#dc2626"

    lu = (parcel.get("LAND USE") or "").upper() if parcel else ""
    is_vacant = "VACANT" in lu
    is_multi = "MULTI" in lu
    yoy = mkt.get("yoy", 0)
    cap = financials.get("cap_rate", 0) if financials else 0
    coc = financials.get("coc", 0) if financials else 0
    dscr = financials.get("dscr", 0) if financials else 0
    noi = financials.get("noi", 0) if financials else 0
    dom = mkt.get("dom", 99)

    if is_vacant and yoy > 5:
        hbu = "Ground-Up Development"
        strategy = "Redevelop"
    elif is_vacant:
        hbu = "Land Bank or Entitled Development"
        strategy = "Wait for better pricing"
    elif is_multi and cap > 5:
        hbu = "Value-Add Multifamily"
        strategy = "Buy and improve"
    elif coc > 6 and dscr > 1.25:
        hbu = "Cash-Flowing Investment"
        strategy = "Hold existing asset"
    elif yoy > 6 and dom < 30:
        hbu = "Appreciation Play"
        strategy = "Buy and improve"
    elif overall < 40:
        hbu = "Re-evaluate or Reposition"
        strategy = "Avoid"
    else:
        hbu = "Stabilized Hold"
        strategy = "Hold existing asset"

    reasons = []
    if yoy > 5:
        reasons.append(("Strong Appreciation", "+{}% YoY growth exceeds inflation, signaling sustained demand".format(yoy)))
    if dom < 30:
        reasons.append(("Fast Market", "{} days on market indicates seller's market with buyer urgency".format(dom)))
    if nb and nb.get("oz"):
        reasons.append(("Opportunity Zone", "Capital gains deferral provides meaningful tax advantage for long-term holders"))
    if cap > 5:
        reasons.append(("Strong Cap Rate", "{:.1f}% cap rate exceeds market average, income-generating potential".format(cap)))
    if coc > 5:
        reasons.append(("Positive Cash-on-Cash", "{:.1f}% CoC return delivers cash flow from day one".format(coc)))
    if loc > 65:
        reasons.append(("Prime Location", "Walk/transit/bike scores position this in a desirable, connected neighborhood"))
    if mkt.get("absorption", 0) > 75:
        reasons.append(("Strong Absorption", "{}% absorption rate means new supply is being digested efficiently".format(mkt.get("absorption", 0))))
    if demo.get("income", 0) > 55000:
        reasons.append(("High Area Income", "${:,} median income supports premium rents and buyer pool".format(demo.get("income", 0))))
    if dscr > 1.3:
        reasons.append(("Healthy DSCR", "{:.2f}x debt coverage gives lender comfort and safety margin".format(dscr)))
    if mkt.get("inv_mo", 99) < 3:
        reasons.append(("Low Inventory", "{} months supply is a seller's market condition".format(mkt.get("inv_mo", 0))))
    while len(reasons) < 5:
        reasons.append(("Data Needed", "Additional due diligence required to validate this factor"))

    red_flags = []
    if nb:
        flood = nb.get("flood", "")
        if "VE" in flood:
            red_flags.append(("High Flood Risk", "VE zone means high-velocity coastal flooding and $8K-$15K+/yr insurance"))
        elif "AE" in flood:
            red_flags.append(("Moderate Flood Risk", "AE zone requires flood insurance at $2K-$6K/yr"))
        if nb.get("crime", 0) > 60:
            red_flags.append(("Elevated Crime", "Crime index {}/100 may deter some tenants and buyers".format(nb.get("crime", 0))))
    if cap < 4 and cap > 0:
        red_flags.append(("Low Cap Rate", "{:.1f}% cap rate means thin yield margin".format(cap)))
    if dscr > 0 and dscr < 1.0:
        red_flags.append(("Negative Cash Flow", "DSCR {:.2f}x means income doesn't cover debt service".format(dscr)))
    if dom > 60:
        red_flags.append(("Slow Market", "{} DOM suggests oversupply or overpricing in the area".format(dom)))
    if mkt.get("inv_mo", 0) > 6:
        red_flags.append(("Excess Inventory", "{} months supply signals buyer's market with pricing pressure".format(mkt.get("inv_mo", 0))))
    if mkt.get("units_pipeline", 0) > 500 and mkt.get("absorption", 100) < 70:
        red_flags.append(("Supply Risk", "{:,} units in pipeline with {}% absorption".format(mkt.get("units_pipeline", 0), mkt.get("absorption", 0))))
    if data_sc < 50:
        red_flags.append(("Low Data Confidence", "Only {}% of data verified. Key inputs may be estimated".format(data_sc)))
    while len(red_flags) < 3:
        red_flags.append(("Insufficient Data", "Cannot fully assess without additional verified data sources"))

    missing = []
    if not parcel:
        missing.append("Official parcel record / folio number")
    if not financials:
        missing.append("Rent assumptions and financial inputs")
    if data_sc < 50:
        missing.append("Verified property data sources")
    if comps_count < 3:
        missing.append("Sufficient comparable sales (minimum 3)")
    if not nb:
        missing.append("Neighborhood market data")
    if not parcel or not parcel.get("YEAR BUILT") or str(parcel.get("YEAR BUILT", "0")) == "0":
        missing.append("Building age and condition assessment")
    if not missing:
        missing.append("All primary data available")

    dd_steps = [
        "Order a Phase I Environmental Site Assessment",
        "Obtain a certified appraisal from a licensed MAI appraiser",
        "Review title report and survey for encumbrances",
        "Verify zoning compliance with City Planning Department",
        "Inspect physical condition and obtain repair estimates",
        "Review 3 years of operating statements if income property",
        "Confirm flood zone and insurance requirements with FEMA",
        "Engage local broker for current market comparable analysis",
    ]

    if coc > 8:
        scenario_rec = "Upside"
        scenario_detail = "Strong fundamentals support optimistic assumptions"
    elif coc > 3:
        scenario_rec = "Base"
        scenario_detail = "Balanced assumptions are appropriate given market conditions"
    else:
        scenario_rec = "Conservative"
        scenario_detail = "Proceed with downside protection as primary consideration"

    risk_adj_return = max(coc * 0.8 - 1.5, 0) if coc else 0

    memo_parts = []
    memo_parts.append("This property at {} presents a {} investment profile".format(
        geo.get("display", "the subject address"),
        verdict.lower()))
    if nb_name:
        memo_parts.append(" within the {} submarket".format(nb_name))
    memo_parts.append(".")

    if yoy > 5:
        memo_parts.append(" The area is experiencing strong momentum at +{}% year-over-year appreciation.".format(yoy))
    if noi > 0:
        memo_parts.append(" At the current rent level, the property generates {} in annual NOI".format(format_currency(noi)))
        memo_parts.append(" representing a {:.1f}% cap rate.".format(cap))

    if strategy == "Buy and improve":
        memo_parts.append(" The recommended approach is to acquire and implement a value-add program to increase rents and reduce vacancy.")
    elif strategy == "Hold existing asset":
        memo_parts.append(" The asset is performing well and a hold strategy maximizes current cash flow while benefiting from appreciation.")
    elif strategy == "Redevelop":
        memo_parts.append(" Given the vacant land and favorable zoning, ground-up development offers the highest return potential.")
    elif strategy == "Avoid":
        memo_parts.append(" Current risk factors outweigh potential returns. We recommend monitoring for improved conditions.")

    investor_take = ""
    if verdict == "Strong Opportunity":
        investor_take = "I would move quickly on this deal. The combination of market momentum, income potential, and location fundamentals creates a compelling entry point. Secure financing and begin due diligence immediately."
    elif verdict == "Watch":
        investor_take = "This has potential but needs validation. I would complete a thorough due diligence process before committing capital. Negotiate aggressively on price and build in contingencies."
    elif verdict == "Needs More Data":
        investor_take = "I would not commit capital until key data gaps are filled. The investment thesis cannot be properly validated with current information. Fill the missing data items first."
    elif verdict == "Proceed with Caution":
        investor_take = "This deal requires careful underwriting. I would stress-test the assumptions with conservative inputs and only proceed if the numbers work under pessimistic scenarios."
    else:
        investor_take = "I would pass on this deal in its current form. The risk-reward profile does not justify capital deployment. Look for better opportunities in adjacent markets."

    return {
        "verdict": verdict,
        "verdict_color": verdict_color,
        "hbu": hbu,
        "strategy": strategy,
        "reasons": reasons[:5],
        "red_flags": red_flags[:5],
        "missing": missing,
        "dd_steps": dd_steps,
        "scenario_rec": scenario_rec,
        "scenario_detail": scenario_detail,
        "risk_adj_return": risk_adj_return,
        "memo": "".join(memo_parts),
        "investor_take": investor_take,
        "overall": overall,
        "scores": scores or {},
    }
