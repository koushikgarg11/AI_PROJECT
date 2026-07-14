import streamlit as st
import os

st.set_page_config(
    page_title="TalentScreen AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 3rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
    }

    .main-header h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -1px;
    }

    .main-header p {
        color: #a78bfa;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    .accent-badge {
        display: inline-block;
        background: #7c3aed;
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .feature-card {
        background: #1e1b4b;
        border: 1px solid #312e81;
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        transition: border-color 0.2s;
    }

    .feature-card:hover {
        border-color: #7c3aed;
    }

    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .feature-card h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #e2e8f0;
        font-size: 1rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    .feature-card p {
        color: #94a3b8;
        font-size: 0.85rem;
        margin: 0;
        line-height: 1.5;
    }

    .workflow-step {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem;
        background: #0f172a;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        border-left: 3px solid #7c3aed;
    }

    .step-num {
        background: #7c3aed;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: opacity 0.2s;
        width: 100%;
    }

    .stButton > button:hover {
        opacity: 0.9;
        border: none;
    }

    /* Dark sidebar */
    [data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid #1e293b;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="accent-badge">AI-Powered Recruitment</div>
    <h1>🎯 TalentScreen AI</h1>
    <p>Upload resumes → AI shortlists → Candidates fill smart assessment forms</p>
</div>
""", unsafe_allow_html=True)

# Feature cards
col1, col2, col3, col4 = st.columns(4)
features = [
    ("🤖", "AI Shortlisting", "Claude AI reads resumes and scores candidates against your criteria"),
    ("📋", "Smart Questions", "Generates tailored questions based on each candidate's skills & projects"),
    ("🎥", "Video Responses", "2 communication skill questions answered via video upload"),
    ("📊", "HR Dashboard", "Review all submissions with scores and assessments in one place"),
]
for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navigation buttons
st.markdown("### Get Started")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏢 HR Portal — Upload & Screen Resumes"):
        st.switch_page("pages/1_HR_Portal.py")
with c2:
    if st.button("📝 Candidate Portal — Fill Assessment Form"):
        st.switch_page("pages/2_Candidate_Form.py")
with c3:
    if st.button("📊 Dashboard — View All Submissions"):
        st.switch_page("pages/3_Dashboard.py")

st.markdown("<br>", unsafe_allow_html=True)

# How it works
st.markdown("### How It Works")
steps = [
    ("HR sets job criteria", "Define role, required skills, experience level, and qualifications"),
    ("Upload resumes (PDF/DOCX)", "Batch upload up to 50 resumes at once"),
    ("AI screens & shortlists", "Claude AI scores each resume and selects top candidates"),
    ("Candidates receive form link", "Shortlisted candidates get a personalized assessment link"),
    ("Smart questions generated", "AI creates questions from their actual skills and projects"),
    ("Video communication check", "2 questions require video responses to assess soft skills"),
    ("HR reviews submissions", "Dashboard shows all responses, scores, and video links"),
]
for i, (title, desc) in enumerate(steps, 1):
    st.markdown(f"""
    <div class="workflow-step">
        <div class="step-num">{i}</div>
        <div>
            <strong style="color:#e2e8f0">{title}</strong><br>
            <span style="color:#94a3b8; font-size:0.85rem">{desc}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
