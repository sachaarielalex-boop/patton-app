"""PATTON Assistant — a 100% FREE voice-driven co-pilot (no API key, no account).

Voice in: streamlit_mic_recorder.speech_to_text (free browser speech recognition).
Voice out: the browser's speechSynthesis (free).
"Brain": a local intent parser (regex/keywords) — no paid LLM. It understands
commands and drives the app: owner search, address analysis, portfolio, leases,
navigation. Bilingual (English / French) keywords.
"""
import json
import re
import datetime
import streamlit as st


# ── Intent parsing (the free "brain") ─────────────────────────────────────
_PAGES = {
    "home": ["home", "accueil", "menu principal"],
    "property": ["property search", "recherche de propriété", "property page"],
    "office": ["office suite", "suite finder", "bureau"],
    "buildings": ["building", "buildings", "immeuble", "immeubles"],
    "brokers": ["broker", "brokers", "courtier", "courtiers"],
    "tenants": ["tenant folder", "tenants", "locataire", "locataires", "folders"],
    "calendar": ["calendar", "calendrier", "lease contract", "leases"],
    "marketing": ["marketing"],
    "sales": ["monthly goal", "objectif", "sales goal"],
    "projects": ["project", "projects", "projet", "projets"],
}


def _extract_after(text, triggers):
    for t in triggers:
        m = re.search(t + r"\s+(?:of\s+|for\s+|by\s+|de\s+|du\s+|named\s+)?(.+)", text)
        if m:
            return m.group(1).strip(" ?.!").strip()
    return ""


def parse_intent(raw):
    """Return (reply_text, action_dict_or_None) for a spoken/typed command."""
    text = (raw or "").strip()
    low = text.lower()
    if not low:
        return "I didn't catch that, sir.", None

    # 1) Owner search ─ "who owns X", "owner X", "qui possède X", "owned by X"
    owner = _extract_after(low, [r"who owns", r"qui poss[eè]de", r"propri[ée]taire",
                                 r"owned by", r"propri[ée]t[ée]s de", r"owner"])
    if owner and any(k in low for k in ["own", "propri"]):
        from utils.property_data import search_by_owner
        res = search_by_owner(owner)
        if not res:
            return "I found no properties for {}, sir.".format(owner), None
        names = ", ".join(r["address"] for r in res[:3] if r.get("address"))
        reply = "{} owns {} propert{}. For example: {}.".format(
            owner.upper(), len(res), "y" if len(res) == 1 else "ies", names)
        return reply, {"type": "owner", "query": owner, "count": len(res)}

    # 2) Lease expirations ─ "leases in 2027", "baux qui finissent"
    if any(k in low for k in ["lease", "leases", "bail", "baux", "expir", "contract"]):
        ym = re.search(r"\b(20\d{2})\b", low)
        year = int(ym.group(1)) if ym else None
        from page_calendar import _collect_contracts
        rows = [c for c in _collect_contracts() if c.get("end")]
        if year:
            rows = [c for c in rows if c["end"].year == year]
        if not rows:
            return ("No leases end in {}.".format(year) if year
                    else "I have no dated leases on file."), None
        rows.sort(key=lambda c: c["end"])
        sample = "; ".join("{} ({})".format(c.get("name"), c["end"].year) for c in rows[:3])
        when = "in {}".format(year) if year else "on record"
        return "{} lease{} {}. Such as: {}.".format(
            len(rows), "" if len(rows) == 1 else "s", when, sample), None

    # 3) Portfolio / occupancy summary
    if any(k in low for k in ["portfolio", "occupancy", "occupation", "portefeuille",
                              "vacant", "how many building"]):
        from utils.buildings_inventory import get_all_buildings
        bs = get_all_buildings()
        if bs:
            avg = sum(b["occupancy"] for b in bs) / len(bs)
            rsf = sum(b["building_rsf"] for b in bs)
            avail = sum(1 for b in bs for s in b["suites"]
                        if s["status"] in ("vacant", "expired"))
            return ("The portfolio has {} buildings, {:,} square feet, {:.0f}% average "
                    "occupancy, and {} available suites.".format(len(bs), rsf, avg, avail)), None

    # 4) Analyze an address ─ "analyze X", "analyse X", or a street-looking phrase
    addr = _extract_after(low, [r"analy[sz]e?r?", r"look at", r"property at",
                                r"adresse", r"regarde"])
    if not addr and re.search(r"\b\d{2,6}\b.*\b(ave|avenue|st|street|road|rd|blvd|drive|dr|ter|terrace|ct|court|place|pl|way)\b", low):
        addr = text  # the whole utterance looks like an address
    if addr and any(k in low for k in ["analy", "look at", "property at", "adresse", "regarde"]) \
            or (addr and re.search(r"\b\d", addr)):
        # Re-cut from the original (preserve casing/numbers) when possible.
        cut = _extract_after(text, [r"(?i)analy[sz]e?r?", r"(?i)look at",
                                    r"(?i)property at", r"(?i)adresse", r"(?i)regarde"])
        addr = cut or addr
        return "Opening the full analysis for {}, sir.".format(addr), \
            {"type": "analyze", "address": addr}

    # 5) Navigation ─ "go to X", "open X", "ouvre X"
    if any(k in low for k in ["go to", "open", "ouvre", "va ", "show me", "montre",
                              "navigate", "take me"]):
        for page, kws in _PAGES.items():
            if any(kw in low for kw in kws):
                return "Opening {}, sir.".format(page), {"type": "navigate", "page": page}

    # 6) Greetings / help
    if any(k in low for k in ["hello", "hey", "bonjour", "salut", "are you there"]):
        return ("At your service, sir. Ask me to search an owner, analyze an address, "
                "summarize the portfolio, check lease expirations, or open a section."), None
    if any(k in low for k in ["help", "what can you", "aide", "commands"]):
        return ("You can say: 'who owns Tristar', 'analyze 2700 NW 2 Ave', "
                "'portfolio occupancy', 'leases in 2027', or 'open buildings'."), None

    return ("I'm not certain how to help with that, sir. Try 'who owns…', 'analyze…', "
            "'portfolio', 'leases in 2027', or 'open buildings'."), None


# ── Voice output (free browser speech synthesis) ──────────────────────────
def _speak(text):
    if not text:
        return
    import streamlit.components.v1 as components
    payload = json.dumps(text)
    components.html(
        "<script>"
        "var t = {payload};"
        "function go() {{"
        "  var synth = window.parent.speechSynthesis; if (!synth) return;"
        "  var vs = synth.getVoices();"
        "  var u = new SpeechSynthesisUtterance(t);"
        "  var pick = vs.find(function(v){{return /en-GB/.test(v.lang) && /(daniel|arthur|george|male)/i.test(v.name);}})"
        "    || vs.find(function(v){{return /en-GB/.test(v.lang);}}) || vs[0];"
        "  if (pick) u.voice = pick; u.rate = 0.97; u.pitch = 0.9;"
        "  synth.cancel(); synth.speak(u);"
        "}}"
        "if (window.parent.speechSynthesis.getVoices().length) go();"
        "else window.parent.speechSynthesis.onvoiceschanged = go;"
        "</script>".format(payload=payload),
        height=0,
    )


# ── Arc-reactor orb ───────────────────────────────────────────────────────
def _orb(state):
    colors = {"idle": "#2563eb", "listening": "#06b6d4",
              "thinking": "#7c3aed", "speaking": "#22c55e"}
    c = colors.get(state, "#2563eb")
    label = {"idle": "Standing by", "listening": "Listening…",
             "thinking": "Thinking…", "speaking": "Speaking…"}.get(state, "")
    st.markdown(
        "<style>"
        "@keyframes orbPulse {{0%,100%{{transform:scale(1);opacity:.85}}50%{{transform:scale(1.08);opacity:1}}}}"
        "@keyframes orbSpin {{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}}"
        ".orb-wrap{{display:flex;flex-direction:column;align-items:center;gap:.6rem;margin:.5rem 0 1.2rem;}}"
        ".orb{{width:120px;height:120px;border-radius:50%;position:relative;"
        "background:radial-gradient(circle at 50% 45%, {c} 0%, rgba(2,6,23,.9) 70%);"
        "box-shadow:0 0 40px -4px {c},inset 0 0 26px -6px {c};animation:orbPulse 2.6s ease-in-out infinite;}}"
        ".orb::before{{content:'';position:absolute;inset:10px;border-radius:50%;"
        "border:2px solid {c};border-top-color:transparent;border-bottom-color:transparent;"
        "animation:orbSpin 4s linear infinite;opacity:.8;}}"
        ".orb::after{{content:'';position:absolute;inset:30px;border-radius:50%;"
        "border:1.5px solid {c};border-left-color:transparent;animation:orbSpin 2.4s linear infinite reverse;}}"
        ".orb-label{{font-size:.7rem;letter-spacing:2px;text-transform:uppercase;color:{c};font-weight:700;}}"
        "</style>"
        "<div class='orb-wrap'><div class='orb'></div><div class='orb-label'>{label}</div></div>".format(
            c=c, label=label),
        unsafe_allow_html=True,
    )


# ── Page ──────────────────────────────────────────────────────────────────
def render_assistant_page():
    from utils.style import inject_css, LOGO_B64
    inject_css()

    if st.sidebar.button("Back to Home", key="asst_back"):
        st.session_state["app_mode"] = "home"
        st.rerun()

    logo_tag = ""
    if LOGO_B64:
        logo_tag = '<img src="data:image/png;base64,{}" style="height:50px;">'.format(LOGO_B64)
    st.markdown(
        '<div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.5rem;">'
        '{logo}<div><h2 style="margin:0;color:var(--text-primary);">PATTON Assistant</h2>'
        '<div style="font-size:0.75rem;color:var(--text-muted);">Free voice co-pilot &mdash; no account, no key</div>'
        '</div></div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    _orb(st.session_state.get("_assistant_state", "idle"))

    # Input: free browser mic if the package is present, else type.
    user_text = None
    try:
        from streamlit_mic_recorder import speech_to_text
        st.caption("Tap the mic and speak (Chrome/Edge), or type below.")
        user_text = speech_to_text(language="en", start_prompt="🎙️ Speak to PATTON",
                                   stop_prompt="⏹ Stop", just_once=True, key="asst_stt")
    except Exception:
        st.caption("Type your command below. (Voice input needs the streamlit-mic-recorder package.)")
    typed = st.chat_input("Ask PATTON… e.g. 'who owns Tristar', 'analyze 2700 NW 2 Ave'")
    if typed:
        user_text = typed

    history = st.session_state.setdefault("assistant_display", [])
    for m in history:
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.markdown(m["text"])

    if user_text:
        history.append({"role": "user", "text": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
        reply, action = parse_intent(user_text)
        with st.chat_message("assistant"):
            st.markdown(reply)
        history.append({"role": "assistant", "text": reply})
        if len(history) > 30:
            del history[:len(history) - 30]
        _speak(reply)
        st.session_state["_assistant_state"] = "speaking"
        if action:
            _render_action_button(action)


def _render_action_button(action):
    t = action.get("type")
    if t == "owner":
        if st.button("Show the {} properties →".format(action.get("count", "")),
                     type="primary", key="asst_do_owner", use_container_width=True):
            st.session_state["owner_query"] = action.get("query", "")
            st.session_state["app_mode"] = "property"
            st.rerun()
    elif t == "analyze":
        addr = action.get("address", "")
        if st.button("Open analysis for {} →".format(addr), type="primary",
                     key="asst_do_analyze", use_container_width=True):
            st.session_state["_rand_addr"] = addr
            st.session_state["_auto_analyze"] = True
            st.session_state["app_mode"] = "property"
            st.rerun()
    elif t == "navigate":
        page = action.get("page", "home")
        if st.button("Open {} →".format(page.title()), type="primary",
                     key="asst_do_nav", use_container_width=True):
            st.session_state["app_mode"] = page
            st.rerun()
