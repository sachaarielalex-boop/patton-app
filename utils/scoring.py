def compute_scores(geo, nb, records, financials=None):
    scores = {"location": 50, "market": 50, "financial": 50, "risk": 50, "data_confidence": 30, "overall": 50}
    if not nb:
        return scores

    m = nb.get("mkt", {})
    d = nb.get("demo", {})
    s = nb.get("scores", {})

    loc = 0
    loc += min(s.get("walk", 0), 100) * 0.35
    loc += min(s.get("transit", 0), 100) * 0.25
    loc += min(s.get("bike", 0), 100) * 0.15
    loc += max(0, 100 - nb.get("crime", 50)) * 0.25
    scores["location"] = int(loc)

    mkt = 0
    yoy = m.get("yoy", 0)
    mkt += min(yoy * 8, 40)
    mkt += min(m.get("absorption", 0) * 0.4, 35)
    if m.get("dom", 99) < 30: mkt += 15
    elif m.get("dom", 99) < 60: mkt += 8
    mkt += 10 if nb.get("oz") else 0
    scores["market"] = min(int(mkt), 100)

    risk = 100
    risk -= nb.get("crime", 50) * 0.4
    if "VE" in nb.get("flood", ""): risk -= 25
    elif "AE" in nb.get("flood", ""): risk -= 12
    if m.get("inv_mo", 0) > 6: risk -= 15
    scores["risk"] = max(int(risk), 10)

    if financials:
        fin = 50
        coc = financials.get("coc", 0)
        if coc > 10: fin = 85
        elif coc > 7: fin = 70
        elif coc > 4: fin = 55
        elif coc > 0: fin = 40
        else: fin = 20
        dscr = financials.get("dscr", 0)
        if dscr >= 1.5: fin += 10
        elif dscr < 1.0: fin -= 20
        scores["financial"] = min(max(int(fin), 10), 100)

    conf = 40
    if geo.get("lat"): conf += 20
    if records: conf += 20
    if nb: conf += 15
    if financials: conf += 5
    scores["data_confidence"] = min(conf, 100)

    scores["overall"] = int(
        scores["location"] * 0.25 +
        scores["market"] * 0.20 +
        scores["financial"] * 0.25 +
        scores["risk"] * 0.15 +
        scores["data_confidence"] * 0.15
    )
    return scores
