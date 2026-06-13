def compute_financials(inputs):
    p = inputs["purchase"]
    dp_pct = inputs["down_pct"]
    ir = inputs["rate"]
    term = inputs["term"]
    rent = inputs["rent"]
    n_units = inputs["units"]
    vac_pct = inputs["vacancy"]
    opex_pct = inputs["opex_pct"]
    tax_rate = inputs["tax_rate"]
    ins_rate = inputs.get("ins_rate", 0.5)
    mgmt_pct = inputs["mgmt_pct"]

    dn = p * dp_pct / 100
    loan = p - dn
    mr = ir / 100 / 12
    n = term * 12
    pmt = loan * (mr * (1 + mr) ** n) / ((1 + mr) ** n - 1) if mr > 0 else loan / max(n, 1)

    ga = rent * n_units * 12
    vac_loss = ga * vac_pct / 100
    egi = ga - vac_loss
    tax = p * tax_rate / 100
    ins = p * ins_rate / 100
    maint = p * 0.01
    mgmt = egi * mgmt_pct / 100
    opex = tax + ins + maint + mgmt
    noi = egi - opex
    ds = pmt * 12
    cf = noi - ds
    cap = noi / p * 100 if p else 0
    coc = cf / dn * 100 if dn else 0
    dscr = noi / ds if ds else 0
    grm = p / ga if ga else 0
    be = (opex + ds) / ga * 100 if ga else 0
    val_from_cap = noi / (inputs.get("exit_cap", cap) / 100) if inputs.get("exit_cap", cap) else 0

    return {
        "down_payment": dn, "loan": loan, "monthly_pmt": pmt,
        "gross_rent": ga, "vacancy_loss": vac_loss, "egi": egi,
        "tax": tax, "insurance": ins, "maintenance": maint, "management": mgmt,
        "opex": opex, "noi": noi, "debt_service": ds, "cash_flow": cf,
        "cap_rate": cap, "coc": coc, "dscr": dscr, "grm": grm,
        "breakeven": be, "val_from_cap": val_from_cap,
    }

def sensitivity_table(base_inputs, vary_key, vary_values, output_key):
    rows = []
    for v in vary_values:
        inp = dict(base_inputs)
        inp[vary_key] = v
        out = compute_financials(inp)
        rows.append({"input": v, "output": out[output_key]})
    return rows
