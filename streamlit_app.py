import streamlit as st
import requests
import os

# -----------------------------------------------
# Config
# -----------------------------------------------
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="CineLex AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d;
    color: #f0ede6;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; }

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: -1px;
    line-height: 1;
    color: #f0ede6;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-size: 0.95rem;
    font-weight: 300;
    color: #888;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}
.accent { color: #e8b86d; }

.answer-card {
    background: #141414;
    border: 1px solid #222;
    border-left: 3px solid #e8b86d;
    border-radius: 8px;
    padding: 1.4rem 1.6rem;
    font-size: 0.97rem;
    line-height: 1.75;
    white-space: pre-wrap;
    margin-top: 1rem;
}
.answer-meta {
    display: flex;
    gap: 12px;
    margin-top: 0.9rem;
    font-size: 0.73rem;
    color: #555;
}
.meta-pill {
    background: #1a1a1a;
    border: 1px solid #262626;
    border-radius: 12px;
    padding: 3px 10px;
    color: #777;
}
.meta-pill span { color: #e8b86d; font-weight: 500; }

.stTextInput > div > div > input {
    background: #111 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #f0ede6 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #e8b86d !important;
    box-shadow: 0 0 0 2px rgba(232,184,109,0.12) !important;
}
.stButton > button {
    background: #e8b86d !important;
    color: #0d0d0d !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.8rem !important;
    cursor: pointer !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

.divider { border: none; border-top: 1px solid #1f1f1f; margin: 1.5rem 0; }

.history-item {
    padding: 0.55rem 0;
    border-bottom: 1px solid #1a1a1a;
    font-size: 0.85rem;
    color: #666;
}
.history-q { font-weight: 500; color: #888; }
.history-a { color: #555; font-size: 0.8rem; margin-top: 2px; }

.sidebar-stat {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.82rem;
    color: #666;
}
.sidebar-stat .val { color: #e8b86d; font-size: 1.1rem; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Session state
# -----------------------------------------------
for key, default in [
    ("history", []),
    ("prefill", ""),
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
    except requests.exceptions.ConnectionError:
        return None, f"Cannot reach API at `{API_URL}`. Is the server running?"
    except requests.exceptions.Timeout:
        return None, "Request timed out (>120s). Try again."
    except Exception as e:
        return None, str(e)

# -----------------------------------------------
# Sidebar
# -----------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Playfair Display\',serif;font-size:1.4rem;'
        'color:#f0ede6;margin-bottom:1.2rem">Cine<span style="color:#e8b86d">'
        'Lex</span> <span style="font-size:0.8rem;color:#555">AI</span></div>',
        unsafe_allow_html=True
    )

    total_q   = len(st.session_state.history)
    analytics = sum(1 for h in st.session_state.history if h["route"] == "analytics")
    rag_count = total_q - analytics

    st.markdown(
        f'<div class="sidebar-stat">Queries this session'
        f'<div class="val">{total_q}</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="sidebar-stat">📊 Analytics / 🎬 RAG'
        f'<div class="val">{analytics} / {rag_count}</div></div>',
        unsafe_allow_html=True
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.7rem;color:#333">'
        'LangGraph · CrewAI · Groq · ChromaDB · SQLite · MLflow'
        '</div>',
        unsafe_allow_html=True
    )

# -----------------------------------------------
# Hero
# -----------------------------------------------
st.markdown("""
<div class="hero-title">Cine<span class="accent">Lex</span></div>
<div class="hero-sub">AI · Movie Intelligence</div>
""", unsafe_allow_html=True)

# -----------------------------------------------
# Suggestion chips
# -----------------------------------------------
SUGGESTIONS = [
    "Top 10 movies by rating",
    "Tell me about Inception",
    "Best Christopher Nolan films",
    "Worst rated movies",
    "Latest releases",
    "Highest grossing movies",
]

cols = st.columns(len(SUGGESTIONS))
for i, sug in enumerate(SUGGESTIONS):
    with cols[i % len(SUGGESTIONS)]:
        if st.button(sug, key=f"chip_{i}"):
            st.session_state.prefill = sug

# -----------------------------------------------
# Input
# -----------------------------------------------
query = st.text_input(
    label="query",
    value=st.session_state.prefill,
    placeholder="Ask anything about movies…",
    label_visibility="collapsed",
    key="query_input"
)

col_btn, col_clear = st.columns([1, 6])
with col_btn:
    search_clicked = st.button("Ask →")
with col_clear:
    if st.session_state.history and st.button("Clear history", key="clear_hist"):
        st.session_state.history = []
        st.rerun()

# -----------------------------------------------
# Query execution
# -----------------------------------------------
if search_clicked and query.strip():
    st.session_state.prefill = ""

    with st.spinner("Thinking…"):
        data, err = call_api(query.strip())

    if err:
        st.error(err)
    else:
        answer = data.get("answer", "").strip()
        route  = data.get("route",  "unknown")
        source = data.get("source", "unknown")

        st.session_state.history.insert(0, {
            "query":  query.strip(),
            "answer": answer,
            "route":  route,
            "source": source,
        })

# -----------------------------------------------
# Results
# -----------------------------------------------
if st.session_state.history:
    latest     = st.session_state.history[0]
    route_icon = "📊" if latest["route"] == "analytics" else "🎬"

    st.markdown(
        f'<div class="answer-card">{latest["answer"]}</div>'
        f'<div class="answer-meta">'
        f'  <div class="meta-pill">mode <span>{route_icon} {latest["route"]}</span></div>'
        f'  <div class="meta-pill">source <span>{latest["source"]}</span></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------
    # History
    # -----------------------------------------------
    if len(st.session_state.history) > 1:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.75rem;text-transform:uppercase;'
            'letter-spacing:0.08em;color:#444;margin-bottom:0.6rem">'
            'Recent questions</div>',
            unsafe_allow_html=True
        )
        for item in st.session_state.history[1:8]:
            r_icon = "📊" if item["route"] == "analytics" else "🎬"
            ans_preview = (item["answer"][:120] + "…") if len(item["answer"]) > 120 else item["answer"]
            st.markdown(
                f'<div class="history-item">'
                f'<div class="history-q">{r_icon} {item["query"]}</div>'
                f'<div class="history-a">{ans_preview}</div>'
                f'</div>',
                unsafe_allow_html=True
            )