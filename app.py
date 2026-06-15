"""
AI Resume Shortlister & Interview Form Generator
Main entry point — handles API key setup and navigation.
"""

import streamlit as st
from backend.gemini_client import validate_api_key, initialize_gemini, FALLBACK_MODELS
from backend import storage

# ── Auto-load saved API key on first run ──────────────────────────────────────
if not st.session_state.get("gemini_ready"):
    saved_key = storage.load_api_key()
    if saved_key:
        try:
            client = initialize_gemini(saved_key)
            # Quick validate to find the first working model
            valid, working_model = validate_api_key(saved_key)
            if valid:
                st.session_state["raw_api_key"] = saved_key
                st.session_state["gemini_model"] = client
                st.session_state["gemini_ready"] = True
                st.session_state.setdefault("preferred_model", working_model)
        except Exception:
            pass  # Key may have expired; user will need to re-enter

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Hire | Resume Shortlister",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Base Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d18 0%, #0a0a14 100%) !important;
    border-right: 1px solid rgba(124, 58, 237, 0.2);
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #a78bfa !important;
}

/* ── Main background ── */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1100px;
}

/* ── Hero Section ── */
.hero-container {
    background: linear-gradient(135deg, #1a0533 0%, #0d1b3e 50%, #0a0a14 100%);
    border: 1px solid rgba(124, 58, 237, 0.3);
    border-radius: 20px;
    padding: 3.5rem 3rem;
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(124, 58, 237, 0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #94a3b8;
    max-width: 600px;
    margin: 0 auto 1.5rem;
    line-height: 1.7;
}

/* ── Feature Cards ── */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    margin: 2rem 0;
}
.feature-card {
    background: rgba(18, 18, 30, 0.8);
    border: 1px solid rgba(124, 58, 237, 0.2);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}
.feature-card:hover {
    border-color: rgba(124, 58, 237, 0.5);
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(124, 58, 237, 0.15);
}
.feature-icon {
    font-size: 2.2rem;
    margin-bottom: 0.75rem;
    display: block;
}
.feature-title {
    font-weight: 600;
    color: #e2e8f0;
    font-size: 1rem;
    margin-bottom: 0.4rem;
}
.feature-desc {
    color: #64748b;
    font-size: 0.85rem;
    line-height: 1.5;
}

/* ── API Key Card ── */
.api-card {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(16, 185, 129, 0.05) 100%);
    border: 1px solid rgba(124, 58, 237, 0.3);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
}
.api-card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #a78bfa;
    margin-bottom: 0.5rem;
}

/* ── Status Badges ── */
.badge-success {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #34d399;
    padding: 0.3rem 0.9rem;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 500;
}
.badge-warning {
    display: inline-block;
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.4);
    color: #fbbf24;
    padding: 0.3rem 0.9rem;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 500;
}
.badge-error {
    display: inline-block;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #f87171;
    padding: 0.3rem 0.9rem;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 500;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s ease !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: rgba(18, 18, 30, 0.9) !important;
    border: 1px solid rgba(124, 58, 237, 0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124, 58, 237, 0.4), transparent);
    margin: 2rem 0;
}

/* ── Step Badge ── */
.step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: linear-gradient(135deg, #7c3aed, #6d28d9);
    border-radius: 50%;
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    margin-right: 0.6rem;
}

/* ── Info box ── */
.info-box {
    background: rgba(96, 165, 250, 0.08);
    border-left: 3px solid #60a5fa;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    color: #93c5fd;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AI Hire")
    st.markdown("---")
    st.markdown("**Navigation**")
    st.page_link("app.py", label="🏠 Home & Setup", icon=None)
    st.page_link("pages/1_Recruiter_Dashboard.py", label="📋 Recruiter Dashboard")
    st.page_link("pages/2_Candidate_Form.py", label="📝 Candidate Form")
    st.page_link("pages/3_View_Responses.py", label="👁️ View Responses")
    st.markdown("---")

    # API Key status
    if st.session_state.get("gemini_ready"):
        st.markdown('<span class="badge-success">✅ Gemini Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-warning">⚠️ API Key Needed</span>', unsafe_allow_html=True)
    st.markdown("")
    st.caption("Powered by Google Gemini 2.5 Flash")


# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🤖 AI Hire</div>
    <div class="hero-subtitle">
        Intelligent resume shortlisting & automated interview question generation
        powered by Google Gemini AI
    </div>
</div>
""", unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <span class="feature-icon">📄</span>
        <div class="feature-title">Smart Shortlisting</div>
        <div class="feature-desc">Upload multiple resumes. Gemini AI scores and ranks candidates against your custom criteria.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🧠</span>
        <div class="feature-title">Personalized Questions</div>
        <div class="feature-desc">Auto-generates skill, project & scenario questions unique to each candidate's background.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🎥</span>
        <div class="feature-title">Video Responses</div>
        <div class="feature-desc">Candidates upload video answers to 2 communication questions. Review everything in one place.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── API Key Setup ─────────────────────────────────────────────────────────────
st.markdown("### 🔑 Step 1 — Connect Google Gemini")

if st.session_state.get("gemini_ready"):
    # ── Already connected ──────────────────────────────────────────────────────
    active_model = st.session_state.get("preferred_model", "gemini-1.5-flash")
    st.markdown(f"""
    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 14px; padding: 1.5rem 2rem; margin-bottom: 1rem;">
        <div style="display:flex;align-items:center;gap:0.75rem;">
            <span style="font-size:1.8rem;">✅</span>
            <div style="flex:1;">
                <div style="color:#34d399;font-weight:700;font-size:1.05rem;">Gemini Connected &amp; API Key Saved</div>
                <div style="color:#64748b;font-size:0.85rem;margin-top:0.2rem;">
                    Active model: <strong style="color:#a78bfa;">{active_model}</strong>
                    &nbsp;|&nbsp; Key saved locally — auto-loads on restart
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Model selector
    model_col, change_col = st.columns([3, 1])
    with model_col:
        model_labels = {
            "gemini-2.5-flash":    "gemini-2.5-flash  —  ⭐ Newest & Recommended",
            "gemini-2.0-flash-lite":"gemini-2.0-flash-lite  —  Fast, separate quota",
            "gemini-1.5-flash":    "gemini-1.5-flash  —  Stable fallback",
            "gemini-1.5-flash-8b": "gemini-1.5-flash-8b  —  Lightweight fallback",
            "gemini-2.0-flash":    "gemini-2.0-flash  —  Capable (may hit quota)",
        }
        chosen = st.selectbox(
            "🧠 Preferred AI Model (auto-fallback if quota exceeded)",
            options=list(model_labels.keys()),
            format_func=lambda m: model_labels[m],
            index=list(model_labels.keys()).index(active_model)
                  if active_model in model_labels else 0,
            key="model_selector",
        )
        if chosen != active_model:
            st.session_state["preferred_model"] = chosen
            st.rerun()
    with change_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Change Key", use_container_width=True):
            storage.clear_api_key()
            st.session_state.pop("raw_api_key", None)
            st.session_state.pop("gemini_model", None)
            st.session_state.pop("preferred_model", None)
            st.session_state["gemini_ready"] = False
            st.rerun()
    st.markdown("""
    <div class="info-box" style="margin-top:0.75rem;">
        ⚡ If you see a <strong>quota error</strong>, select a different model above —
        each model has its own independent free-tier quota.
        Or wait a few minutes for the limit to reset.
    </div>
    """, unsafe_allow_html=True)
else:
    # ── Need to connect ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="info-box">
        🔐 Enter your Gemini API key below. It will be <strong>saved locally on this machine</strong>
        so you never need to re-enter it after the first time.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="api-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="api-card-title">Google Gemini API Key</div>', unsafe_allow_html=True)
        api_key_input = st.text_input(
            label="API Key",
            type="password",
            placeholder="AIza...",
            value="",
            label_visibility="collapsed",
            key="api_key_field",
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        connect_btn = st.button("🔌 Connect & Save", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if connect_btn and api_key_input:
        with st.spinner("Verifying API key (no quota consumed)..."):
            valid, result = validate_api_key(api_key_input)

        if not valid:
            st.error(f"❌ {result}")

        elif result == "quota_exhausted":
            # Key is real but ALL models are temporarily rate-limited
            storage.save_api_key(api_key_input)
            st.session_state["raw_api_key"] = api_key_input
            st.session_state["gemini_model"] = initialize_gemini(api_key_input)
            st.session_state["gemini_ready"] = True
            st.session_state["preferred_model"] = "gemini-2.5-flash"
            st.warning(
                "⚠️ **API key saved successfully!** Your key is valid, but all Gemini models "
                "have hit their free-tier rate limit right now.\n\n"
                "**What to do:** Wait a few minutes (limits reset every minute/hour/day) "
                "then refresh the page — the app will work automatically. "
                "Or get a new key at [Google AI Studio](https://aistudio.google.com/app/apikey)."
            )
            st.rerun()

        else:
            # Key is valid AND a working model was found
            working_model = result
            storage.save_api_key(api_key_input)
            st.session_state["raw_api_key"] = api_key_input
            st.session_state["gemini_model"] = initialize_gemini(api_key_input)
            st.session_state["gemini_ready"] = True
            st.session_state["preferred_model"] = working_model
            st.success(f"✅ Connected using **{working_model}**. Key saved — won't ask again.")
            st.rerun()

    elif connect_btn and not api_key_input:
        st.warning("Please enter your API key first.")


# ── How It Works ──────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 📖 How It Works")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="feature-card" style="text-align:left;">
        <div><span class="step-badge">1</span><strong style="color:#e2e8f0">Recruiter Setup</strong></div>
        <ul style="color:#64748b; font-size:0.85rem; margin-top:0.75rem; padding-left:1.2rem;">
            <li>Define job title & criteria</li>
            <li>Set required skills & experience</li>
            <li>Upload batch of resumes (PDF/DOCX)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="feature-card" style="text-align:left;">
        <div><span class="step-badge">2</span><strong style="color:#e2e8f0">AI Analysis</strong></div>
        <ul style="color:#64748b; font-size:0.85rem; margin-top:0.75rem; padding-left:1.2rem;">
            <li>Gemini scores each resume</li>
            <li>Auto-shortlists top candidates</li>
            <li>Generates unique interview form links</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="feature-card" style="text-align:left;">
        <div><span class="step-badge">3</span><strong style="color:#e2e8f0">Candidate & Review</strong></div>
        <ul style="color:#64748b; font-size:0.85rem; margin-top:0.75rem; padding-left:1.2rem;">
            <li>Candidate fills personalized form</li>
            <li>Uploads 2 video answers</li>
            <li>Recruiter reviews all responses</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ── Get API Key Link ──────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
    📌 Don't have a Gemini API key? Get one free at 
    <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #a78bfa;">
    Google AI Studio</a>
</div>
""", unsafe_allow_html=True)
