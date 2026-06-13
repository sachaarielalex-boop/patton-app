import os

def generate_summary(addr, geo, nb_name, nb, scores, financials=None, records=None):
    key = os.getenv("OPENAI_API_KEY", "")
    if key:
        return _openai_summary(key, addr, geo, nb_name, nb, scores, financials, records)
    return _template_summary(addr, geo, nb_name, nb, scores, financials, records)

def _template_summary(addr, geo, nb_name, nb, scores, financials=None, records=None):
    overall = scores.get("overall", 50)
    if overall >= 75:
        verdict = "STRONG BUY"
        verdict_class = "alert-ok"
        tone = "This property presents a compelling investment opportunity with strong fundamentals across multiple dimensions."
    elif overall >= 55:
        verdict = "MODERATE BUY"
        verdict_class = "alert-info"
        tone = "This property shows solid potential with some areas requiring additional due diligence."
    elif overall >= 40:
        verdict = "HOLD / CONDITIONAL"
        verdict_class = "alert-warn"
        tone = "This property has mixed signals. Proceed with caution and validate key assumptions."
    else:
        verdict = "PASS"
        verdict_class = "alert-err"
        tone = "Current metrics do not support an investment thesis at this time."

    mkt = nb.get("mkt", {}) if nb else {}
    demo = nb.get("demo", {}) if nb else {}

    sections = []
    sections.append('<div class="{}"><b>AI VERDICT: {}</b></div>'.format(verdict_class, verdict))
    sections.append('<div class="card"><div class="card-title">Executive Summary</div>')
    sections.append('<p style="font-size:0.85rem;color:var(--slate-700);line-height:1.7;">')
    sections.append(tone)

    if nb_name:
        sections.append(' The subject property is located in <b>{}</b>'.format(nb_name))
        if nb:
            sections.append(', {}'.format(nb.get("tagline", "")))
        sections.append('.')

    if mkt:
        sections.append(' The local market shows <b>{}% YoY appreciation</b>'.format(mkt.get("yoy", "N/A")))
        sections.append(' with median pricing at <b>${:,}/sqft</b>'.format(mkt.get("psf", 0)))
        sections.append(' and average days on market of <b>{}</b>.'.format(mkt.get("dom", "N/A")))

    if nb and nb.get("oz"):
        sections.append(' <b>Opportunity Zone designation</b> provides meaningful tax benefits for qualified investors.')

    sections.append('</p></div>')

    sections.append('<div class="card"><div class="card-title">Score Breakdown</div>')
    sections.append('<table class="dtable">')
    for label, key in [("Location", "location"), ("Market", "market"), ("Financial", "financial"), ("Risk", "risk"), ("Data Confidence", "data_confidence")]:
        v = scores.get(key, 50)
        c = "var(--green)" if v >= 70 else ("var(--amber)" if v >= 40 else "var(--red)")
        sections.append('<tr><td class="dk">{}</td><td class="dv" style="color:{};">{}/100</td></tr>'.format(label, c, v))
    sections.append('<tr style="border-top:2px solid var(--slate-300);"><td class="dk" style="font-weight:700;">Overall</td>')
    oc = "var(--green)" if overall >= 70 else ("var(--amber)" if overall >= 40 else "var(--red)")
    sections.append('<td class="dv" style="color:{};font-size:1.1rem;">{}/100</td></tr>'.format(oc, overall))
    sections.append('</table></div>')

    if financials:
        sections.append('<div class="card"><div class="card-title">Financial Highlights</div>')
        sections.append('<table class="dtable">')
        sections.append('<tr><td class="dk">Net Operating Income</td><td class="dv">${:,.0f}</td></tr>'.format(financials.get("noi", 0)))
        sections.append('<tr><td class="dk">Cap Rate</td><td class="dv">{:.1f}%</td></tr>'.format(financials.get("cap_rate", 0)))
        sections.append('<tr><td class="dk">Cash-on-Cash Return</td><td class="dv">{:.1f}%</td></tr>'.format(financials.get("coc", 0)))
        sections.append('<tr><td class="dk">DSCR</td><td class="dv">{:.2f}x</td></tr>'.format(financials.get("dscr", 0)))
        sections.append('</table></div>')

    sections.append('<div class="card"><div class="card-title">Key Risks</div><ul style="font-size:0.82rem;color:var(--slate-700);line-height:1.8;margin:0;padding-left:1.2rem;">')
    risks = nb.get("risks", []) if nb else ["Insufficient data for risk assessment"]
    for r in risks:
        sections.append('<li>{}</li>'.format(r))
    sections.append('</ul></div>')

    sections.append('<div class="card"><div class="card-title">Investment Highlights</div><ul style="font-size:0.82rem;color:var(--slate-700);line-height:1.8;margin:0;padding-left:1.2rem;">')
    highlights = nb.get("highlights", []) if nb else ["Further analysis required"]
    for h in highlights:
        sections.append('<li>{}</li>'.format(h))
    sections.append('</ul></div>')

    sections.append('<div class="alert-info" style="margin-top:1rem;font-size:0.7rem;">This summary was generated using template-based analysis. Connect an OpenAI API key for AI-powered narrative analysis. <span class="placeholder-tag">DEMO</span></div>')

    return "\n".join(sections)

def _openai_summary(key, addr, geo, nb_name, nb, scores, financials, records):
    try:
        import openai
        client = openai.OpenAI(api_key=key)
        prompt = "You are an expert Miami-Dade real estate investment analyst. Write a concise (300 words max) investment summary for the property at {}.\n\n".format(addr)
        prompt += "Neighborhood: {}\n".format(nb_name or "Unknown")
        prompt += "Overall Score: {}/100\n".format(scores.get("overall", "N/A"))
        prompt += "Location: {}/100, Market: {}/100, Financial: {}/100, Risk: {}/100\n".format(
            scores.get("location", "N/A"), scores.get("market", "N/A"),
            scores.get("financial", "N/A"), scores.get("risk", "N/A"))
        if nb:
            mkt = nb.get("mkt", {})
            prompt += "Median Price: ${:,}, PSF: ${}, Yield: {}%, YoY: {}%\n".format(
                mkt.get("med_price", 0), mkt.get("psf", 0), mkt.get("yield", 0), mkt.get("yoy", 0))
        if financials:
            prompt += "NOI: ${:,.0f}, Cap Rate: {:.1f}%, CoC: {:.1f}%, DSCR: {:.2f}x\n".format(
                financials.get("noi", 0), financials.get("cap_rate", 0),
                financials.get("coc", 0), financials.get("dscr", 0))
        prompt += "\nProvide: 1) Verdict (Buy/Hold/Pass), 2) Key strengths, 3) Key risks, 4) Recommended strategy."

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        text = resp.choices[0].message.content
        html = '<div class="card"><div class="card-title">AI Investment Analysis</div>'
        html += '<div style="font-size:0.85rem;color:var(--slate-700);line-height:1.7;white-space:pre-wrap;">{}</div>'.format(text)
        html += '</div>'
        return html
    except Exception as e:
        return '<div class="alert-err">OpenAI API error: {}. Falling back to template.</div>\n'.format(str(e)) + _template_summary(addr, geo, nb_name, nb, scores, financials, records)
