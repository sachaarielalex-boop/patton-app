"""PATTON Assistant — a voice-driven, Jarvis-style AI that pilots the app.

Push-to-talk (free browser speech) -> Claude (with tools over PATTON's own data) ->
spoken reply via the browser's speech synthesis + an animated arc-reactor orb.

Setup required (Streamlit secrets or env):
  ANTHROPIC_API_KEY = "sk-ant-..."
Optional package for the mic button (falls back to typing if absent):
  streamlit-mic-recorder
"""
import json
import streamlit as st

ASSISTANT_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = (
    "You are the PATTON Assistant, a calm, concise, British-butler-style AI for a "
    "Miami-Dade commercial real-estate intelligence app called PATTON. You help the "
    "user analyze properties, find owners, and review the building portfolio and "
    "leases. Use the tools to answer with real data — never invent folios, owners or "
    "numbers. Keep spoken replies short and natural (1-3 sentences); the user hears "
    "them aloud. When the user wants to open or analyze something, call the matching "
    "action tool. Address the user politely (e.g. 'sir' sparingly, like a butler)."
)

TOOLS = [
    {"name": "search_owner",
     "description": "Find all Miami-Dade properties owned by a person or company name.",
     "input_schema": {"type": "object",
                      "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "portfolio_summary",
     "description": "Summary of Patton's owned building portfolio: buildings, RSF, occupancy, vacant suites.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "lease_expirations",
     "description": "List leases that expire, optionally filtered to a single year.",
     "input_schema": {"type": "object",
                      "properties": {"year": {"type": "integer"}}}},
    {"name": "analyze_address",
     "description": "Open PATTON's full analysis for a specific Miami-Dade address. Use when the user wants to analyze/look at a property.",
     "input_schema": {"type": "object",
                      "properties": {"address": {"type": "string"}}, "required": ["address"]}},
    {"name": "navigate",
     "description": "Open a section of the app.",
     "input_schema": {"type": "object",
                      "properties": {"page": {"type": "string",
                          "enum": ["home", "property", "office", "buildings", "brokers",
                                   "tenants", "calendar", "marketing", "sales", "projects"]}},
                      "required": ["page"]}},
]


# ── Tool implementations ──────────────────────────────────────────────────
def _run_tool(name, inp):
    inp = inp or {}
    try:
        if name == "search_owner":
            from utils.property_data import search_by_owner
            res = search_by_owner(inp.get("name", ""))[:15]
            if not res:
                return "No properties found for that owner."
            return json.dumps([{"address": r.get("address"), "owner": r.get("owner"),
                                "folio": r.get("folio")} for r in res])

        if name == "portfolio_summary":
            from utils.buildings_inventory import get_all_buildings
            bs = get_all_buildings()
            data = []
            for b in bs:
                avail = sum(1 for s in b["suites"] if s["status"] in ("vacant", "expired"))
                data.append({"name": b["name"], "rsf": b["building_rsf"],
                             "occupancy": b["occupancy"], "available_suites": avail})
            return json.dumps(data)

        if name == "lease_expirations":
            from page_calendar import _collect_contracts
            year = inp.get("year")
            rows = []
            for c in _collect_contracts():
                end = c.get("end")
                if not end:
                    continue
                if year and end.year != int(year):
                    continue
                rows.append({"tenant": c.get("name"), "building": c.get("building"),
                             "suite": c.get("suite"), "ends": end.isoformat()})
            rows.sort(key=lambda r: r["ends"])
            if not rows:
                return "No leases match." if year else "No dated leases found."
            return json.dumps(rows[:25])

        if name == "analyze_address":
            addr = (inp.get("address") or "").strip()
            st.session_state["_assistant_action"] = {"type": "analyze", "address": addr}
            return "Ready to open the analysis for {}.".format(addr)

        if name == "navigate":
            page = inp.get("page", "home")
            st.session_state["_assistant_action"] = {"type": "navigate", "page": page}
            return "Ready to open {}.".format(page)
    except Exception as e:  # tools must never crash the turn
        return "Tool error: {}".format(e)
    return "Unknown tool."


def _ask_claude(user_text):
    """Run one user turn through Claude with the tool loop. Returns the reply text."""
    import anthropic
    key = _get_key()
    client = anthropic.Anthropic(api_key=key)

    msgs = st.session_state.setdefault("assistant_api_msgs", [])
    msgs.append({"role": "user", "content": user_text})

    final = ""
    for _ in range(6):  # cap tool round-trips
        resp = client.messages.create(
            model=ASSISTANT_MODEL, max_tokens=1024, system=SYSTEM_PROMPT,
            tools=TOOLS, messages=msgs,
        )
        if resp.stop_reason == "tool_use":
            msgs.append({"role": "assistant", "content": resp.content})
            results = []
            for block in resp.content:
                if getattr(block, "type", None) == "tool_use":
                    out = _run_tool(block.name, block.input)
                    results.append({"type": "tool_result", "tool_use_id": block.id,
                                    "content": out})
            msgs.append({"role": "user", "content": results})
            continue
        final = "".join(getattr(b, "text", "") for b in resp.content
                        if getattr(b, "type", None) == "text")
        msgs.append({"role": "assistant", "content": resp.content})
        break

    # Keep history bounded.
    if len(msgs) > 24:
        del msgs[:len(msgs) - 24]
    return final or "I'm not sure how to help with that, sir."


def _get_key():
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    import os
    return os.environ.get("ANTHROPIC_API_KEY", "")


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
        '<div style="font-size:0.75rem;color:var(--text-muted);">Your voice-driven real-estate co-pilot</div>'
        '</div></div>'.format(logo=logo_tag),
        unsafe_allow_html=True,
    )

    if not _get_key():
        st.warning(
            "Voice assistant needs an Anthropic API key. Add **ANTHROPIC_API_KEY** in "
            "your Streamlit app **Settings → Secrets** (or as an environment variable), "
            "then reload.")
        st.code('ANTHROPIC_API_KEY = "sk-ant-..."', language="toml")
        return

    state = st.session_state.get("_assistant_state", "idle")
    _orb(state)

    # Input: mic button if available, else text.
    user_text = None
    try:
        from streamlit_mic_recorder import speech_to_text
        st.caption("Tap the mic and speak, or type below.")
        user_text = speech_to_text(language="en", start_prompt="🎙️ Speak to PATTON",
                                   stop_prompt="⏹ Stop", just_once=True, key="asst_stt")
    except Exception:
        st.caption("Type your request (install streamlit-mic-recorder for voice input).")
    typed = st.chat_input("Ask PATTON…")
    if typed:
        user_text = typed

    # Conversation transcript.
    history = st.session_state.setdefault("assistant_display", [])
    for m in history:
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.markdown(m["text"])

    if user_text:
        history.append({"role": "user", "text": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)
        st.session_state["_assistant_state"] = "thinking"
        with st.chat_message("assistant"):
            with st.spinner("PATTON is thinking…"):
                reply = _ask_claude(user_text)
            st.markdown(reply)
        history.append({"role": "assistant", "text": reply})
        _speak(reply)
        st.session_state["_assistant_state"] = "speaking"

        # Apply any action the assistant decided on.
        action = st.session_state.pop("_assistant_action", None)
        if action:
            _render_action_button(action)


def _render_action_button(action):
    if action.get("type") == "analyze":
        addr = action.get("address", "")
        if st.button("Open analysis for {} →".format(addr), type="primary",
                     key="asst_do_analyze", use_container_width=True):
            st.session_state["_rand_addr"] = addr
            st.session_state["_auto_analyze"] = True
            st.session_state["app_mode"] = "property"
            st.rerun()
    elif action.get("type") == "navigate":
        page = action.get("page", "home")
        if st.button("Open {} →".format(page.title()), type="primary",
                     key="asst_do_nav", use_container_width=True):
            st.session_state["app_mode"] = page
            st.rerun()
