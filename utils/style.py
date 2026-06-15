import streamlit as st
import base64, os

def get_logo_b64():
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

LOGO_B64 = get_logo_b64()

# ═══════════════════════════════════════════════════════
# THEME SYSTEM – Light / Dark
# ═══════════════════════════════════════════════════════

LIGHT_VARS = """
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #f1f5f9;
    --bg-card: #ffffff;
    --bg-sidebar: #0f172a;
    --bg-glass: rgba(255,255,255,0.85);
    --bg-input: #ffffff;
    --border: #e2e8f0;
    --border-hover: #cbd5e1;
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-tertiary: #64748b;
    --text-muted: #94a3b8;
    --text-inverse: #ffffff;
    --accent: #2563eb;
    --accent-hover: #1d4ed8;
    --accent-soft: #eff6ff;
    --accent-border: rgba(37,99,235,0.2);
    --green: #059669;
    --green-soft: #ecfdf5;
    --green-border: rgba(5,150,105,0.2);
    --red: #dc2626;
    --red-soft: #fef2f2;
    --red-border: rgba(220,38,38,0.2);
    --amber: #d97706;
    --amber-soft: #fffbeb;
    --amber-border: rgba(217,119,6,0.2);
    --gold: #c9a96e;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
    --shadow-lg: 0 8px 30px rgba(0,0,0,0.08);
    --radius: 12px;
    --radius-sm: 8px;
    --radius-xs: 6px;
    /* Legacy aliases for backward compat */
    --navy: #0f172a;
    --navy-light: #1e293b;
    --slate-700: #334155;
    --slate-500: #64748b;
    --slate-400: #94a3b8;
    --slate-300: #cbd5e1;
    --slate-200: #e2e8f0;
    --slate-100: #f1f5f9;
    --slate-50: #f8fafc;
    --white: #ffffff;
    --blue: #2563eb;
    --blue-light: #3b82f6;
    --blue-50: #eff6ff;
    --green-50: #ecfdf5;
    --red-50: #fef2f2;
    --amber-50: #fffbeb;
"""

DARK_VARS = """
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --bg-card: #1e293b;
    --bg-sidebar: #020617;
    --bg-glass: rgba(15,23,42,0.9);
    --bg-input: #1e293b;
    --border: #334155;
    --border-hover: #475569;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-tertiary: #94a3b8;
    --text-muted: #64748b;
    --text-inverse: #0f172a;
    --accent: #3b82f6;
    --accent-hover: #60a5fa;
    --accent-soft: rgba(59,130,246,0.12);
    --accent-border: rgba(59,130,246,0.3);
    --green: #34d399;
    --green-soft: rgba(52,211,153,0.1);
    --green-border: rgba(52,211,153,0.25);
    --red: #f87171;
    --red-soft: rgba(248,113,113,0.1);
    --red-border: rgba(248,113,113,0.25);
    --amber: #fbbf24;
    --amber-soft: rgba(251,191,36,0.1);
    --amber-border: rgba(251,191,36,0.25);
    --gold: #d4af37;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 30px rgba(0,0,0,0.5);
    --radius: 12px;
    --radius-sm: 8px;
    --radius-xs: 6px;
    /* Legacy aliases - remapped for dark mode */
    --navy: #f1f5f9;
    --navy-light: #e2e8f0;
    --slate-700: #cbd5e1;
    --slate-500: #94a3b8;
    --slate-400: #64748b;
    --slate-300: #475569;
    --slate-200: #334155;
    --slate-100: #1e293b;
    --slate-50: #0f172a;
    --white: #1e293b;
    --blue: #3b82f6;
    --blue-light: #60a5fa;
    --blue-50: rgba(59,130,246,0.12);
    --green-50: rgba(52,211,153,0.1);
    --red-50: rgba(248,113,113,0.1);
    --amber-50: rgba(251,191,36,0.1);
"""

CSS_BODY = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── App shell ─────────────────────────────── */
#MainMenu, footer { visibility: hidden !important; height: 0 !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.stApp { background: var(--bg-secondary) !important; }
.block-container { padding: 1rem 2rem 2rem !important; max-width: 1400px; position: relative; }
iframe { border: none !important; }

/* ── Page top accent line ──────────────────── */
.block-container::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--gold) 100%);
    z-index: 999;
    opacity: 0.9;
}

/* ── Global animations ─────────────────────── */
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.card, .kpi-card, .scenario-card, .chart-card, .verdict-box, .addr-result {
    animation: fadeUp 0.4s ease both;
}

/* ── Sidebar ───────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    min-width: 260px !important;
    max-width: 300px !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span {
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.68rem !important;
    line-height: 1.45 !important;
    letter-spacing: 0.3px !important;
}
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stSelectbox label {
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    color: rgba(255,255,255,0.45) !important;
    margin-bottom: 0.25rem !important;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h4,
section[data-testid="stSidebar"] .stMarkdown h5 {
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,0.55) !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    margin: 0.6rem 0 0.3rem !important;
}
section[data-testid="stSidebar"] .stMarkdown div {
    font-size: 0.68rem !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}
section[data-testid="stSidebar"] .element-container {
    margin-bottom: 0.25rem !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.95) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-sm);
    padding: 0.7rem 1rem;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.2) !important;
}
section[data-testid="stSidebar"] .stTextInput input::placeholder { color: #94a3b8 !important; }
section[data-testid="stSidebar"] .stTextInput label { color: rgba(255,255,255,0.5) !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.5) !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm);
    padding: 0.7rem;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3);
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--accent-hover) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(37,99,235,0.4);
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.95) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: var(--radius-sm);
    color: #0f172a !important;
}
section[data-testid="stSidebar"] .stSelectbox svg { fill: #64748b !important; }

/* ── Main content buttons ──────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent) 0%, #1d4ed8 100%) !important;
    border: none !important;
    border-radius: var(--radius-sm);
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #fff !important;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25);
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(37,99,235,0.35);
}

/* ── Secondary buttons (Quick Access tabs) ── */
.stButton > button[kind="secondary"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 0.72rem;
    letter-spacing: 0.5px;
    color: var(--text-secondary) !important;
    transition: all 0.2s;
    box-shadow: var(--shadow-sm);
    padding: 0.6rem 1rem;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--accent-soft) !important;
    border-color: var(--accent-border) !important;
    color: var(--accent) !important;
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

/* ── App Header ────────────────────────────── */
.app-header {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.8rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(10px);
}
.app-header .hd-left { display: flex; align-items: center; gap: 1rem; }
.app-header .hd-left img { height: 42px; }
.app-header .hd-title { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.3px; }
.app-header .hd-sub { font-size: 0.68rem; color: var(--text-tertiary); letter-spacing: 0.5px; margin-top: 2px; }

/* ── Badges ────────────────────────────────── */
.badge {
    display: inline-block; font-size: 0.58rem; font-weight: 700; letter-spacing: 0.6px;
    padding: 3px 10px; border-radius: 20px; text-transform: uppercase;
}
.badge-blue { background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent-border); }
.badge-green { background: var(--green-soft); color: var(--green); border: 1px solid var(--green-border); }
.badge-amber { background: var(--amber-soft); color: var(--amber); border: 1px solid var(--amber-border); }
.badge-red { background: var(--red-soft); color: var(--red); border: 1px solid var(--red-border); }

/* ── Address Result ────────────────────────── */
.addr-result {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}
.addr-result .ar-addr { font-size: 1.3rem; font-weight: 700; color: var(--text-primary); }
.addr-result .ar-meta { font-size: 0.75rem; color: var(--text-tertiary); margin-top: 0.4rem; display: flex; gap: 1rem; flex-wrap: wrap; }

/* ── KPI Cards ─────────────────────────────── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 0.8rem;
    margin: 1rem 0;
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.3rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--gold));
    opacity: 0;
    transition: opacity 0.2s;
}
.kpi-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.kpi-card:hover::before { opacity: 1; }
.kpi-card .kl { font-size: 0.58rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }
.kpi-card .kv { font-size: 1.4rem; font-weight: 800; color: var(--text-primary); margin-top: 4px; }
.kpi-card .ks { font-size: 0.7rem; color: var(--text-muted); margin-top: 2px; }

/* ── Section Title ─────────────────────────── */
.sec-title {
    font-size: 1rem; font-weight: 700; color: var(--text-primary);
    margin: 1.5rem 0 0.8rem; padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent);
    display: inline-block;
}

/* ── Card ──────────────────────────────────── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
}
.card:hover { box-shadow: var(--shadow-md); }
.card-title {
    font-size: 0.85rem; font-weight: 700; color: var(--text-primary);
    padding-bottom: 0.5rem; margin-bottom: 0.8rem;
    border-bottom: 1px solid var(--border);
}

/* ── Data Table ────────────────────────────── */
.dtable { width: 100%; border-collapse: collapse; }
.dtable tr { border-bottom: 1px solid var(--bg-tertiary); }
.dtable tr:hover { background: var(--bg-secondary); }
.dtable td { padding: 0.55rem 0.5rem; font-size: 0.8rem; }
.dtable .dk { color: var(--text-tertiary); font-weight: 500; }
.dtable .dv { color: var(--text-primary); font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; }

/* ── Alert Boxes ───────────────────────────── */
.alert-info {
    background: var(--accent-soft); border: 1px solid var(--accent-border); border-radius: var(--radius-sm);
    padding: 0.8rem 1rem; font-size: 0.8rem; color: var(--accent); margin: 0.5rem 0;
}
.alert-warn {
    background: var(--amber-soft); border: 1px solid var(--amber-border); border-radius: var(--radius-sm);
    padding: 0.8rem 1rem; font-size: 0.8rem; color: var(--amber); margin: 0.5rem 0;
}
.alert-ok {
    background: var(--green-soft); border: 1px solid var(--green-border); border-radius: var(--radius-sm);
    padding: 0.8rem 1rem; font-size: 0.8rem; color: var(--green); margin: 0.5rem 0;
}
.alert-err {
    background: var(--red-soft); border: 1px solid var(--red-border); border-radius: var(--radius-sm);
    padding: 0.8rem 1rem; font-size: 0.8rem; color: var(--red); margin: 0.5rem 0;
}

/* ── Placeholder ───────────────────────────── */
.placeholder-tag {
    display: inline-block; font-size: 0.58rem; font-weight: 600; color: var(--text-muted);
    background: var(--bg-tertiary); padding: 2px 6px; border-radius: 3px; letter-spacing: 0.5px;
    vertical-align: middle; margin-left: 4px;
}

/* ── Tabs ──────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid var(--border);
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    padding: 0.7rem 1.2rem; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.5px;
    text-transform: uppercase; border-radius: 0; color: var(--text-muted) !important;
    transition: color 0.2s;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-primary) !important; }
.stTabs [aria-selected="true"] { color: var(--text-primary) !important; border-bottom: 3px solid var(--accent) !important; transition: border-bottom 0.25s ease; }

/* ── Metric Override ───────────────────────── */
div[data-testid="stMetric"] label { font-size: 0.62rem !important; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted) !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text-primary) !important; font-weight: 700 !important; }

/* ── Welcome / Home ────────────────────────── */
.welcome {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    min-height: 65vh; text-align: center;
}
.welcome h1 { font-size: 2rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.5px; margin: 1rem 0 0.3rem; }
.welcome .wl { width: 40px; height: 3px; background: var(--accent); border-radius: 2px; }
.welcome .ws { font-size: 0.72rem; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase; margin-top: 0.6rem; }
.welcome .wd { font-size: 0.95rem; color: var(--text-muted); margin-top: 1.5rem; max-width: 500px; line-height: 1.7; }

/* ── Score Bar ─────────────────────────────── */
.score-bar { height: 8px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden; margin-top: 4px; }
.score-fill { height: 100%; border-radius: 4px; }

/* ── Verdict ───────────────────────────────── */
.verdict-box {
    text-align: center; padding: 1.5rem; border-radius: var(--radius);
    border: 2px solid var(--border); background: var(--bg-card); margin: 0.5rem 0;
    box-shadow: var(--shadow-sm);
}
.verdict-label {
    font-size: 0.58rem; color: var(--text-muted); text-transform: uppercase;
    letter-spacing: 2px; font-weight: 700;
}
.verdict-value { font-size: 1.8rem; font-weight: 800; margin: 0.3rem 0; }
.verdict-sub { font-size: 0.75rem; color: var(--text-muted); }

/* ── Ranked List ───────────────────────────── */
.ranked-item {
    display: flex; gap: 0.7rem; padding: 0.65rem 0;
    border-bottom: 1px solid var(--bg-tertiary); align-items: flex-start;
}
.ranked-num {
    min-width: 24px; height: 24px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 700; color: white; flex-shrink: 0;
}
.ranked-body { flex: 1; }
.ranked-title { font-size: 0.82rem; font-weight: 600; color: var(--text-primary); }
.ranked-detail { font-size: 0.75rem; color: var(--text-tertiary); margin-top: 2px; line-height: 1.5; }

/* ── Zoning Check ──────────────────────────── */
.zcheck { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--bg-tertiary); }
.zcheck-label { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); }
.zcheck-badge { font-size: 0.65rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; letter-spacing: 0.5px; }
.zcheck-pass { background: var(--green-soft); color: var(--green); border: 1px solid var(--green-border); }
.zcheck-fail { background: var(--red-soft); color: var(--red); border: 1px solid var(--red-border); }

/* ── Chart Card ────────────────────────────── */
.chart-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1rem; margin-bottom: 0.8rem;
    box-shadow: var(--shadow-sm);
}
.chart-title {
    font-size: 0.78rem; font-weight: 700; color: var(--text-primary);
    margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;
}
.source-tag {
    font-size: 0.55rem; font-weight: 700; color: var(--text-muted);
    background: var(--bg-tertiary); padding: 2px 8px; border-radius: 20px;
    letter-spacing: 0.3px; text-transform: uppercase;
}

/* ── Scenario Cards ────────────────────────── */
.scenario-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 1rem 0; }
.scenario-card {
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1rem; text-align: center; background: var(--bg-card);
    transition: all 0.2s;
}
.scenario-card:hover { box-shadow: var(--shadow-md); }
.scenario-card.active { border-color: var(--accent); border-width: 2px; }
.scenario-label { font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; }
.scenario-value { font-size: 1.4rem; font-weight: 800; color: var(--text-primary); margin: 0.3rem 0; }
.scenario-sub { font-size: 0.7rem; color: var(--text-muted); }

/* ── Expander ──────────────────────────────── */
.stExpander { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }

/* ── Text Input (main area) ────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-input) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important;
}

/* ── Scrollbar ─────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── Expander chevron animation ────────────── */
.stExpander summary svg, details summary svg { transition: transform 0.25s ease; }

/* ── Download button polish ────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--green) 0%, #047857 100%) !important;
    border: none !important; border-radius: var(--radius-sm) !important;
    color: #fff !important; font-weight: 700 !important; letter-spacing: 0.8px !important;
    transition: all 0.2s ease !important; box-shadow: 0 2px 8px rgba(5,150,105,0.25) !important;
}
.stDownloadButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(5,150,105,0.4) !important; }

/* ── Responsive: stack home cards on mobile ── */
@media (max-width: 640px) {
    .block-container { padding: 0.5rem 1rem 1.5rem !important; }
    .kpi-grid { grid-template-columns: 1fr 1fr !important; }
    .scenario-grid { grid-template-columns: 1fr !important; }
}

/* ── Selection ─────────────────────────────── */
::selection { background: rgba(37,99,235,0.2); color: var(--text-primary); }
"""


def inject_css():
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    theme = st.session_state["theme"]
    theme_vars = LIGHT_VARS if theme == "light" else DARK_VARS

    full_css = "<style>\n:root {{\n{vars}\n}}\n{body}\n</style>".format(
        vars=theme_vars, body=CSS_BODY
    )
    st.markdown(full_css, unsafe_allow_html=True)


def theme_toggle():
    """Render theme toggle button aligned to the right."""
    theme = st.session_state.get("theme", "light")
    next_theme = "dark" if theme == "light" else "light"
    label = "\U0001f319 Dark" if theme == "light" else "\u2600\ufe0f Light"

    _spacer, _btn_col = st.columns([0.88, 0.12])
    with _btn_col:
        if st.button(label, key="theme_btn"):
            st.session_state["theme"] = next_theme
            st.rerun()


def kpi(label, value, sub=""):
    s = '<div class="ks">{}</div>'.format(sub) if sub else ""
    return '<div class="kpi-card"><div class="kl">{}</div><div class="kv">{}</div>{}</div>'.format(label, value, s)

def tr(k, v, placeholder=False):
    tag = ' <span class="placeholder-tag">DEMO</span>' if placeholder else ""
    return '<tr><td class="dk">{}</td><td class="dv">{}{}</td></tr>'.format(k, v, tag)

def score_color(v):
    if v >= 70: return "var(--green)"
    if v >= 40: return "var(--amber)"
    return "var(--red)"

def score_bar(label, value, max_val=100):
    pct = min(value / max_val * 100, 100)
    c = score_color(value)
    return (
        '<div style="margin:0.4rem 0;">'
        '<div style="display:flex;justify-content:space-between;font-size:0.72rem;">'
        '<span style="color:var(--text-tertiary);">{}</span>'
        '<span style="font-weight:700;color:var(--text-primary);">{}/{}</span>'
        '</div>'
        '<div class="score-bar"><div class="score-fill" style="width:{}%;background:{};"></div></div>'
        '</div>'
    ).format(label, value, max_val, pct, c)
