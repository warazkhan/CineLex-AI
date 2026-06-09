import streamlit as st
import requests
import os

# -----------------------------------------------
# Config
# -----------------------------------------------
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="CineLex AI — Movie Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght=300;400;600;700&family=Outfit:wght=300;400;500;600&display=swap');

:root {
    --bg:        #ffffff;
    --surface:   #f9f8f6;
    --surface2:  #f2f0ec;
    --border:    #e2ddd6;
    --border2:   #d4cfc7;
    --gold:      #b5803a;
    --gold-soft: #c9955a;
    --gold-dim:  rgba(181,128,58,0.10);
    --text:      #1a1714;
    --text-dim:  #4a4540;
    --text-mute: #9a9188;
    --teal:      #2e7d80;
    --red:       #b84040;
    --red-bg:    #fff5f5;
    --red-border:#f5c0c0;
}

/* Force light background everywhere */
html, body,
[class*="css"],
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

#MainMenu, footer { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem 3rem; max-width: 1100px; }

/* ── HERO ── */
.hero-wrap {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 0.3rem;
    padding-bottom: 1.8rem;
    border-bottom: 1px solid var(--border);
}
.hero-wordmark {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.6rem;
    font-weight: 700;
    letter-spacing: -1.5px;
    line-height: 1;
    color: #1a1714 !important;
}
.hero-wordmark .accent {
    color: #b5803a !important;
}
.hero-tagline {
    font-size: 0.72rem;
    font-weight: 400;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #9a9188 !important;
    margin-top: 0.35rem;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--gold-dim);
    border: 1px solid rgba(181,128,58,0.25);
    border-radius: 20px;
    padding: 5px 13px;
    font-size: 0.71rem;
    letter-spacing: 0.1em;
    color: #b5803a !important;
    font-weight: 500;
}
.hero-badge .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--gold);
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── CHIPS LABEL ── */
.chips-label {
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9a9188 !important;
    margin: 1.8rem 0 0.7rem;
}

/* ── ALL BUTTONS base ── */
.stButton > button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    border-radius: 9px !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    width: 100% !important;

    min-height: 52px !important;
    white-space: normal !important;
    line-height: 1.25 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    padding: 0.4rem 0.5rem !important;

    background: var(--surface2) !important;
    color: #4a4540 !important;
    border: 1px solid var(--border2) !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    border-color: var(--gold) !important;
    color: var(--gold) !important;
    background: var(--gold-dim) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── INPUT ── */
.stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.78rem 3rem 0.78rem 1.1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input::placeholder { color: #9a9188 !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(181,128,58,0.12) !important;
    outline: none !important;
}

/* ── SEARCH WRAPPER — makes × positioning possible ── */
.search-outer {
    position: relative;
    width: 100%;
}
.search-outer .stTextInput {
    width: 100%;
}

/* ── CLEAR (×) button floated inside input ── */
.clear-btn-wrap {
    position: absolute;
    top: 50%;
    right: 10px;
    transform: translateY(-50%);
    z-index: 10;
}
.clear-btn-wrap .stButton > button {
    width: 32px !important;
    min-height: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: var(--border) !important;
    border: none !important;
    color: var(--text-dim) !important;
    font-size: 0.85rem !important;
    line-height: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.clear-btn-wrap .stButton > button:hover {
    background: var(--border2) !important;
    color: var(--text) !important;
    transform: none !important;
    border: none !important;
}

/* ── ASK button override ── */
div[data-testid="column"] [data-testid="stButton-ask_btn"] button,
button[kind="primaryFormSubmit"],
#ask_btn button {
    background: var(--gold) !important;
    color: #ffffff !important;
    border: none !important;
}

/* ── ANSWER CARD ── */
.answer-card {
    background: var(--surface);
    border: 1px solid var(--border2);
    border-left: 3px solid var(--gold);
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    font-size: 0.96rem;
    line-height: 1.8;
    white-space: pre-wrap;
    margin-top: 1.4rem;
    position: relative;
    overflow: hidden;
    color: #1a1714 !important;
}
.answer-card::before {
    content: '\201C';
    font-family: 'Cormorant Garamond', serif;
    font-size: 6rem;
    color: rgba(181,128,58,0.07);
    position: absolute;
    top: -10px; right: 18px;
    line-height: 1;
    pointer-events: none;
}
.answer-query {
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #9a9188 !important;
    margin-bottom: 0.9rem;
}
.answer-query strong { color: #4a4540 !important; font-weight: 500; }
.answer-text { color: #1a1714 !important; }
.answer-meta { display: flex; gap: 10px; margin-top: 1.2rem; flex-wrap: wrap; }
.meta-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.71rem;
    color: #9a9188 !important;
    letter-spacing: 0.05em;
}
.meta-pill .val { color: #b5803a !important; font-weight: 500; }

/* ── DIVIDER ── */
.divider { border: none; border-top: 1px solid var(--border); margin: 2rem 0 1.4rem; }

/* ── HISTORY ── */
.history-label {
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9a9188 !important;
    margin-bottom: 0.8rem;
}
.history-item {
    display: flex; gap: 12px;
    align-items: flex-start;
    padding: 0.7rem 0;
    border-bottom: 1px solid var(--border);
}
.history-icon {
    font-size: 0.8rem; flex-shrink: 0;
    width: 24px; height: 24px;
    border-radius: 6px;
    background: var(--surface2);
    border: 1px solid var(--border2);
    display: flex; align-items: center; justify-content: center;
}
.history-q { font-size: 0.85rem; font-weight: 500; color: #4a4540 !important; margin-bottom: 2px; }
.history-a { font-size: 0.78rem; color: #9a9188 !important; line-height: 1.5; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 1.8rem 1.4rem !important; }
.sb-wordmark {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem; font-weight: 700;
    color: #1a1714 !important;
    margin-bottom: 1.6rem; letter-spacing: -0.5px;
}
.sb-wordmark .accent { color: #b5803a !important; }
.stat-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1.1rem; margin-bottom: 0.7rem;
}
.stat-label { font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: #9a9188 !important; margin-bottom: 0.3rem; }
.stat-val { font-family: 'Cormorant Garamond', serif; font-size: 2rem; font-weight: 600; color: #b5803a !important; line-height: 1; }
.stat-sub { font-size: 0.72rem; color: #9a9188 !important; margin-top: 3px; }
.sb-section-label { font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; color: #9a9188 !important; margin: 1.4rem 0 0.6rem; }
.tech-pills { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 0.3rem; }
.tech-pill {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 6px; padding: 3px 9px;
    font-size: 0.68rem; color: #9a9188 !important; letter-spacing: 0.04em;
}
.route-bar {
    display: flex; border-radius: 8px; overflow: hidden;
    border: 1px solid var(--border); margin-top: 0.5rem; height: 28px;
}
.route-seg { display: flex; align-items: center; justify-content: center; font-size: 0.68rem; font-weight: 500; }
.route-analytics { background: rgba(46,125,128,0.12); color: #2e7d80 !important; }
.route-rag       { background: var(--gold-dim); color: #b5803a !important; }

/* ── EMPTY STATE ── */
.empty-state { text-align: center; padding: 4rem 0 1rem; }
.empty-icon  { font-size: 3rem; margin-bottom: 0.8rem; opacity: 0.25; }
.empty-title { font-size: 0.85rem; letter-spacing: 0.12em; text-transform: uppercase; color: #9a9188 !important; }
.empty-sub   { font-size: 0.78rem; margin-top: 0.5rem; color: #d4cfc7 !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Session state initializations
# -----------------------------------------------
for key, default in [
    ("history",        []),
    ("prefill",        ""),
    ("trigger_search", False),
    ("pending_query",  ""),
    ("widget_version", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------------------------
# API helper
# -----------------------------------------------
def call_api(q: str):
    try:
        r = requests.post(f"{API_URL}/query", json={"query": q}, timeout=120)
        if r.status_code == 200:
            return r.json(), None
        return None, f"API error {r.status_code}: {r.json().get('detail', r.text)}"
    except Exception as e:
        return None, str(e)

# -----------------------------------------------
# Sidebar
# -----------------------------------------------
with st.sidebar:
    st.markdown('<div class="sb-wordmark">Cine<span class="accent">Lex</span></div>', unsafe_allow_html=True)

    total_q   = len(st.session_state.history)
    analytics = sum(1 for h in st.session_state.history if h["route"] == "analytics")
    rag_count = total_q - analytics

    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">Queries this session</div>'
        f'<div class="stat-val">{total_q}</div>'
        f'<div class="stat-sub">since page load</div>'
        f'</div>', unsafe_allow_html=True)

    if total_q > 0:
        ap = int((analytics / total_q) * 100)
        rp = 100 - ap
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-label">Route split</div>'
            f'<div style="display:flex;justify-content:space-between;margin-top:4px">'
            f'<span style="font-size:0.8rem;color:#2e7d80">📊 Analytics <strong>{analytics}</strong></span>'
            f'<span style="font-size:0.8rem;color:#b5803a">🎬 RAG <strong>{rag_count}</strong></span>'
            f'</div>'
            f'<div class="route-bar" style="margin-top:8px">'
            f'<div class="route-seg route-analytics" style="flex:{max(ap,5)}">{ap}%</div>'
            f'<div class="route-seg route-rag"       style="flex:{max(rp,5)}">{rp}%</div>'
            f'</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="stat-card">'
            '<div class="stat-label">Route split</div>'
            '<div class="stat-sub" style="margin-top:4px">No queries yet</div>'
            '</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section-label">Powered by</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tech-pills">'
        '<span class="tech-pill">LangGraph</span>'
        '<span class="tech-pill">CrewAI</span>'
        '<span class="tech-pill">Groq</span>'
        '</div>', unsafe_allow_html=True)

# -----------------------------------------------
# Hero
# -----------------------------------------------
st.markdown("""
<div class="hero-wrap">
  <div>
    <div class="hero-wordmark">Cine<span class="accent">Lex</span> AI</div>
    <div class="hero-tagline">Movie Intelligence Platform</div>
  </div>
  <div>
    <div class="hero-badge"><span class="dot"></span>Live · Powered by Groq</div>
  </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Input row — text box with × button INSIDE it
# -----------------------------------------------

# Open the relative-positioned wrapper
st.markdown('<div class="search-outer">', unsafe_allow_html=True)

query = st.text_input(
    label="query",
    value=st.session_state.prefill,
    placeholder="Ask anything about movies — titles, directors, analytics, recommendations…",
    label_visibility="collapsed",
    key=f"query_box_v{st.session_state.widget_version}"
)

# Only show the × button when there is text
if st.session_state.prefill:
    st.markdown('<div class="clear-btn-wrap">', unsafe_allow_html=True)
    if st.button("✕", key="clear_input", help="Clear search"):
        st.session_state.prefill        = ""
        st.session_state.widget_version += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Close the wrapper
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------
# Ask / Clear-history buttons (below, same as original)
# -----------------------------------------------
col_btn, col_clear, col_spacer = st.columns([1.4, 1.2, 6])
with col_btn:
    if st.button("Ask →", key="ask_btn", use_container_width=True):
        st.session_state.pending_query  = query
        st.session_state.trigger_search = True
with col_clear:
    if st.session_state.history:
        if st.button("Clear history", key="clear_hist", use_container_width=True):
            st.session_state.history        = []
            st.session_state.pending_query  = ""
            st.session_state.prefill        = ""
            st.session_state.widget_version += 1
            st.rerun()

# -----------------------------------------------
# CONDITIONAL SUGGESTIONS (Disappear after first search)
# -----------------------------------------------
if not st.session_state.history:
    SUGGESTIONS = [
        "Top 10 movies by rating",
        "Tell me about Inception",
        "Top 10 directors",
        "Worst rated movies",
        "Latest releases",
        "Highest grossing movies",
    ]

    st.markdown('<div class="chips-label">Try asking</div>', unsafe_allow_html=True)

    chip_cols = st.columns(len(SUGGESTIONS))
    for i, sug in enumerate(SUGGESTIONS):
        with chip_cols[i]:
            if st.button(sug, key=f"chip_{i}", use_container_width=True):
                st.session_state.prefill        = sug
                st.session_state.pending_query  = sug
                st.session_state.trigger_search = True
                st.session_state.widget_version += 1
                st.rerun()

# -----------------------------------------------
# Query execution
# -----------------------------------------------
if st.session_state.trigger_search:
    q = st.session_state.pending_query.strip()
    st.session_state.trigger_search = False

    if q:
        st.session_state.prefill = q
        with st.spinner("Searching the cinematic universe…"):
            data, err = call_api(q)

        if err:
            st.markdown(
                f'<div style="background:#fff5f5;border:1px solid #f5c0c0;'
                f'border-left:3px solid #b84040;border-radius:10px;'
                f'padding:1rem 1.2rem;margin-top:1rem;font-size:0.9rem;color:#b84040">'
                f'⚠️ {err}</div>', unsafe_allow_html=True)
        else:
            st.session_state.history.insert(0, {
                "query":  q,
                "answer": data.get("answer", "").strip(),
                "route":  data.get("route",  "unknown"),
                "source": data.get("source", "unknown"),
            })
            st.rerun()

# -----------------------------------------------
# Results & Empty State Flow
# -----------------------------------------------
if st.session_state.history:
    latest     = st.session_state.history[0]
    route_icon = "📊" if latest["route"] == "analytics" else "🎬"

    st.markdown(
        f'<div class="answer-card">'
        f'<div class="answer-query">You asked · <strong>{latest["query"]}</strong></div>'
        f'<div class="answer-text">{latest["answer"]}</div>'
        f'<div class="answer-meta">'
        f'<div class="meta-pill">Mode <span class="val">{route_icon} {latest["route"].capitalize()}</span></div>'
        f'<div class="meta-pill">Source <span class="val">{latest["source"]}</span></div>'
        f'</div></div>', unsafe_allow_html=True)

    if len(st.session_state.history) > 1:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="history-label">Previous queries</div>', unsafe_allow_html=True)
        for item in st.session_state.history[1:8]:
            r_icon  = "📊" if item["route"] == "analytics" else "🎬"
            preview = (item["answer"][:130] + "…") if len(item["answer"]) > 130 else item["answer"]
            st.markdown(
                f'<div class="history-item">'
                f'<div class="history-icon">{r_icon}</div>'
                f'<div><div class="history-q">{item["query"]}</div>'
                f'<div class="history-a">{preview}</div></div>'
                f'</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">🎬</div>
      <div class="empty-title">Ask a question to get started</div>
      <div class="empty-sub">Try one of the suggestions above</div>
    </div>""", unsafe_allow_html=True)