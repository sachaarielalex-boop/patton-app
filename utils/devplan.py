def compute_dev_plan(inputs):
    lot_sf = inputs.get("lot_sf", 5000)
    far = inputs.get("far", 3.5)
    max_height_ft = inputs.get("max_height_ft", 65)
    max_floors = inputs.get("max_floors", 5)
    floor_eff = inputs.get("floor_efficiency", 0.80)
    rent_eff = inputs.get("rentable_efficiency", 0.85)
    avg_unit_sf = inputs.get("avg_unit_sf", 850)
    res_pct = inputs.get("res_pct", 85)
    office_pct = inputs.get("office_pct", 10)
    retail_pct = inputs.get("retail_pct", 5)
    parking_ratio = inputs.get("parking_ratio", 1.0)
    construction_psf = inputs.get("construction_psf", 250)
    soft_cost_pct = inputs.get("soft_cost_pct", 25)
    land_price = inputs.get("land_price", 0)
    target_rent_res = inputs.get("target_rent_res", 2500)
    target_rent_office = inputs.get("target_rent_office", 35)
    target_rent_retail = inputs.get("target_rent_retail", 40)
    exit_cap = inputs.get("exit_cap", 5.0)
    interest_rate = inputs.get("interest_rate", 7.0)
    ltv = inputs.get("ltv", 65)
    opex_ratio = inputs.get("opex_ratio", 35)

    max_gsf = lot_sf * far
    floor_plate = lot_sf * floor_eff
    floors_by_gsf = max(1, int(max_gsf / floor_plate)) if floor_plate > 0 else 1
    floor_height = 11
    floors_by_height = max(1, int(max_height_ft / floor_height))
    est_floors = min(floors_by_gsf, floors_by_height, max_floors)
    actual_gsf = floor_plate * est_floors
    rentable_sf = actual_gsf * rent_eff

    res_sf = rentable_sf * res_pct / 100
    office_sf = rentable_sf * office_pct / 100
    retail_sf = rentable_sf * retail_pct / 100
    est_units = max(1, int(res_sf / avg_unit_sf)) if avg_unit_sf > 0 else 0
    parking_spaces = int(est_units * parking_ratio)
    parking_sf = parking_spaces * 350

    hard_cost = actual_gsf * construction_psf
    soft_cost = hard_cost * soft_cost_pct / 100
    parking_cost = parking_spaces * 25000
    total_dev_cost = hard_cost + soft_cost + parking_cost + land_price

    annual_res_income = est_units * target_rent_res * 12
    annual_office_income = office_sf * target_rent_office
    annual_retail_income = retail_sf * target_rent_retail
    gross_income = annual_res_income + annual_office_income + annual_retail_income
    vacancy_loss = gross_income * 0.05
    egi = gross_income - vacancy_loss
    opex = egi * opex_ratio / 100
    noi = egi - opex

    value_at_cap = noi / (exit_cap / 100) if exit_cap > 0 else 0
    profit = value_at_cap - total_dev_cost
    return_on_cost = (noi / total_dev_cost * 100) if total_dev_cost > 0 else 0
    yield_on_cost = return_on_cost
    profit_margin = (profit / total_dev_cost * 100) if total_dev_cost > 0 else 0

    loan_amount = total_dev_cost * ltv / 100
    equity = total_dev_cost - loan_amount
    mr = interest_rate / 100 / 12
    n = 30 * 12
    if mr > 0 and n > 0:
        pmt = loan_amount * (mr * (1 + mr) ** n) / ((1 + mr) ** n - 1)
    else:
        pmt = loan_amount / max(n, 1)
    annual_ds = pmt * 12
    dscr = noi / annual_ds if annual_ds > 0 else 0

    zoning_checks = []
    if actual_gsf > max_gsf * 1.01:
        zoning_checks.append({"item": "FAR", "status": "fail", "detail": "Exceeds max GSF by {:,.0f} sqft".format(actual_gsf - max_gsf)})
    else:
        zoning_checks.append({"item": "FAR", "status": "pass", "detail": "{:,.0f} / {:,.0f} sqft ({:.0f}%)".format(actual_gsf, max_gsf, actual_gsf / max(max_gsf, 1) * 100)})

    bldg_height = est_floors * floor_height
    if bldg_height > max_height_ft:
        zoning_checks.append({"item": "Height", "status": "fail", "detail": "{} ft exceeds {} ft limit".format(bldg_height, max_height_ft)})
    else:
        zoning_checks.append({"item": "Height", "status": "pass", "detail": "{} ft / {} ft limit".format(bldg_height, max_height_ft)})

    if est_floors > max_floors:
        zoning_checks.append({"item": "Floors", "status": "fail", "detail": "{} exceeds {} floor limit".format(est_floors, max_floors)})
    else:
        zoning_checks.append({"item": "Floors", "status": "pass", "detail": "{} / {} floors".format(est_floors, max_floors)})

    zoning_checks.append({"item": "Parking", "status": "pass", "detail": "{} spaces at {:.1f} per unit".format(parking_spaces, parking_ratio)})

    return {
        "lot_sf": lot_sf, "far": far, "max_gsf": max_gsf,
        "floor_plate": int(floor_plate), "est_floors": est_floors,
        "actual_gsf": int(actual_gsf), "rentable_sf": int(rentable_sf),
        "res_sf": int(res_sf), "office_sf": int(office_sf), "retail_sf": int(retail_sf),
        "est_units": est_units, "avg_unit_sf": avg_unit_sf,
        "parking_spaces": parking_spaces, "parking_sf": parking_sf,
        "hard_cost": int(hard_cost), "soft_cost": int(soft_cost),
        "parking_cost": int(parking_cost), "land_price": land_price,
        "total_dev_cost": int(total_dev_cost),
        "gross_income": int(gross_income), "vacancy_loss": int(vacancy_loss),
        "egi": int(egi), "opex": int(opex), "noi": int(noi),
        "value_at_cap": int(value_at_cap), "profit": int(profit),
        "profit_margin": profit_margin, "return_on_cost": return_on_cost,
        "yield_on_cost": yield_on_cost,
        "loan_amount": int(loan_amount), "equity": int(equity),
        "annual_ds": int(annual_ds), "dscr": dscr,
        "zoning_checks": zoning_checks,
        "building_height_ft": est_floors * floor_height,
        "max_height_ft": max_height_ft, "max_floors": max_floors,
    }


def scenario_comparison(base_inputs):
    conservative = dict(base_inputs)
    conservative["construction_psf"] = int(base_inputs.get("construction_psf", 250) * 1.15)
    conservative["target_rent_res"] = int(base_inputs.get("target_rent_res", 2500) * 0.90)
    conservative["exit_cap"] = base_inputs.get("exit_cap", 5.0) + 0.75
    conservative["interest_rate"] = base_inputs.get("interest_rate", 7.0) + 0.5

    upside = dict(base_inputs)
    upside["construction_psf"] = int(base_inputs.get("construction_psf", 250) * 0.92)
    upside["target_rent_res"] = int(base_inputs.get("target_rent_res", 2500) * 1.10)
    upside["exit_cap"] = max(base_inputs.get("exit_cap", 5.0) - 0.5, 3.0)
    upside["interest_rate"] = max(base_inputs.get("interest_rate", 7.0) - 0.5, 3.0)

    return {
        "conservative": compute_dev_plan(conservative),
        "base": compute_dev_plan(base_inputs),
        "upside": compute_dev_plan(upside),
    }
