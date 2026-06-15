"""
Page 2 — Candidate Interview Form
Candidates access this page via a unique link containing their candidate_id.
They answer personalized skill/project questions and upload 2 video responses.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from pathlib import Path
from backend import storage

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Interview Form | AI Hire",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.main .block-container { max-width: 820px; padding-top: 2rem; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d18 0%, #0a0a14 100%) !important;
}

/* Hero Banner */
.form-hero {
    background: linear-gradient(135deg, #1a0533 0%, #0d1b3e 60%, #0a1628 100%);
    border: 1px solid rgba(124, 58, 237, 0.3);
    border-radius: 18px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
}
.form-hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.form-hero-sub { color: #64748b; font-size: 0.9rem; margin-top: 0.5rem; }

.candidate-pill {
    display: inline-block;
    background: rgba(124, 58, 237, 0.15);
    border: 1px solid rgba(124, 58, 237, 0.35);
    border-radius: 50px;
    padding: 0.4rem 1.2rem;
    color: #a78bfa;
    font-size: 0.88rem;
    font-weight: 600;
    margin-top: 1rem;
}

/* Question Sections */
.q-section {
    background: rgba(18, 18, 30, 0.85);
    border: 1px solid rgba(124, 58, 237, 0.18);
    border-radius: 16px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
}
.q-section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #a78bfa;
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(124, 58, 237, 0.15);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.question-block {
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.question-block:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}
.question-label {
    font-size: 0.95rem;
    font-weight: 500;
    color: #e2e8f0;
    margin-bottom: 0.6rem;
    line-height: 1.5;
}
.question-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: rgba(124, 58, 237, 0.3);
    border-radius: 50%;
    font-size: 0.75rem;
    font-weight: 700;
    color: #a78bfa;
    margin-right: 0.5rem;
    flex-shrink: 0;
}

/* Video Upload */
.video-card {
    background: rgba(12, 12, 22, 0.9);
    border: 2px dashed rgba(96, 165, 250, 0.3);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    transition: border-color 0.3s;
    margin-top: 0.75rem;
}
.video-card:hover { border-color: rgba(96, 165, 250, 0.6); }
.video-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.video-hint { color: #64748b; font-size: 0.82rem; margin-top: 0.5rem; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
    transform: translateY(-1px) !important;
}

/* Inputs */
.stTextArea > div > div > textarea {
    background: rgba(10, 10, 20, 0.9) !important;
    border: 1px solid rgba(124, 58, 237, 0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: rgba(124, 58, 237, 0.6) !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.1) !important;
}

.info-box {
    background: rgba(96, 165, 250, 0.08);
    border-left: 3px solid #60a5fa;
    border-radius: 0 10px 10px 0;
    padding: 0.85rem 1.1rem;
    color: #93c5fd;
    font-size: 0.88rem;
    margin: 0.75rem 0;
}
.success-box {
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin-top: 1.5rem;
}

.progress-dots {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(124,58,237,0.3); }
.dot.active { background: #7c3aed; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AI Hire")
    st.markdown("---")
    st.page_link("app.py", label="🏠 Home & Setup")
    st.page_link("pages/1_Recruiter_Dashboard.py", label="📋 Recruiter Dashboard")
    st.page_link("pages/2_Candidate_Form.py", label="📝 Candidate Form")
    st.page_link("pages/3_View_Responses.py", label="👁️ View Responses")


# ── Read candidate_id from URL ────────────────────────────────────────────────
params = st.query_params
candidate_id = params.get("candidate_id", "").strip().upper()

# ── Manual Entry Fallback ─────────────────────────────────────────────────────
st.markdown("""
<div class="form-hero">
    <div class="form-hero-title">📝 Candidate Interview Form</div>
    <div class="form-hero-sub">Answer all questions honestly. Your responses will be reviewed by the hiring team.</div>
</div>
""", unsafe_allow_html=True)

if not candidate_id:
    st.markdown('<div class="info-box">🔑 Enter your Candidate ID below (shared by the recruiter) or open the link provided to you.</div>', unsafe_allow_html=True)
    input_col, btn_col = st.columns([3, 1])
    with input_col:
        manual_id = st.text_input("Candidate ID", placeholder="e.g. A1B2C3D4", label_visibility="collapsed")
    with btn_col:
        if st.button("🔍 Load Form", use_container_width=True):
            if manual_id.strip():
                st.query_params["candidate_id"] = manual_id.strip().upper()
                st.rerun()
            else:
                st.warning("Please enter a valid Candidate ID.")
    st.stop()

# ── Load Candidate Data ────────────────────────────────────────────────────────
candidate_data = storage.load_candidate(candidate_id)
if not candidate_data:
    st.error(f"❌ No candidate found with ID **{candidate_id}**. Please check the link or contact the recruiter.")
    if st.button("🔄 Try Again"):
        st.query_params.clear()
        st.rerun()
    st.stop()

# ── Check already submitted ────────────────────────────────────────────────────
existing_response = storage.load_response(candidate_id)
if existing_response:
    st.markdown("""
    <div class="success-box">
        <div style="font-size:3rem;">🎉</div>
        <div style="font-size:1.3rem;font-weight:700;color:#34d399;margin:0.75rem 0;">Form Already Submitted!</div>
        <div style="color:#64748b;">You have already submitted your interview responses. The hiring team will be in touch.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Extract data ───────────────────────────────────────────────────────────────
assessment = candidate_data.get("assessment", {})
questions = candidate_data.get("questions", {})
name = assessment.get("candidate_name", "Candidate")
email = assessment.get("email", "")

skill_qs = questions.get("skill_questions", [])
project_qs = questions.get("project_questions", [])
comm_qs = questions.get("communication_questions", [])

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;margin-bottom:1.5rem;">
    <div class="candidate-pill">👤 {name} &nbsp;|&nbsp; ID: {candidate_id}</div>
</div>
""", unsafe_allow_html=True)

total_questions = len(skill_qs) + len(project_qs) + len(comm_qs)
st.markdown(f'<div class="info-box">📋 This form has <strong>{total_questions} questions</strong> — {len(skill_qs)} skill, {len(project_qs)} project, and {len(comm_qs)} video communication questions. All fields are required.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FORM
# ══════════════════════════════════════════════════════════════════════════════
with st.form("interview_form", clear_on_submit=False):

    text_answers = {}
    video_files = {}

    # ── Skill Questions ────────────────────────────────────────────────────────
    if skill_qs:
        st.markdown('<div class="q-section">', unsafe_allow_html=True)
        st.markdown('<div class="q-section-title">⚡ Technical Skills</div>', unsafe_allow_html=True)

        for i, q in enumerate(skill_qs, 1):
            st.markdown(f"""
            <div class="question-block">
                <div class="question-label">
                    <span class="question-num">{i}</span>{q["question"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            answer = st.text_area(
                label=f"skill_{i}",
                placeholder=q.get("placeholder", "Type your answer here..."),
                height=130,
                label_visibility="collapsed",
                key=f"sq_{q['id']}",
            )
            text_answers[q["id"]] = answer

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Project Questions ──────────────────────────────────────────────────────
    if project_qs:
        st.markdown('<div class="q-section">', unsafe_allow_html=True)
        st.markdown('<div class="q-section-title">🚀 Project Experience</div>', unsafe_allow_html=True)

        for i, q in enumerate(project_qs, 1):
            st.markdown(f"""
            <div class="question-block">
                <div class="question-label">
                    <span class="question-num">{i}</span>{q["question"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            answer = st.text_area(
                label=f"project_{i}",
                placeholder=q.get("placeholder", "Describe your experience..."),
                height=140,
                label_visibility="collapsed",
                key=f"pq_{q['id']}",
            )
            text_answers[q["id"]] = answer

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Communication Questions (Video) ────────────────────────────────────────
    if comm_qs:
        st.markdown('<div class="q-section">', unsafe_allow_html=True)
        st.markdown('<div class="q-section-title">🎥 Communication Skills — Video Responses</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            📹 Record a short video (1–2 minutes) for each question below.
            Accepted formats: MP4, MOV, WEBM, AVI. Max 200MB per file.
        </div>
        """, unsafe_allow_html=True)

        for i, q in enumerate(comm_qs, 1):
            st.markdown(f"""
            <div class="question-block">
                <div class="question-label">
                    <span class="question-num">{i}</span>{q["question"]}
                </div>
                <div class="video-card">
                    <div class="video-icon">🎬</div>
                    <div style="color:#94a3b8;font-size:0.9rem;">Upload your video response</div>
                    <div class="video-hint">MP4 • MOV • WEBM • AVI &nbsp;|&nbsp; Max 200 MB</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            vid = st.file_uploader(
                label=f"Video {i}",
                type=["mp4", "mov", "webm", "avi"],
                key=f"vid_{q['id']}",
                label_visibility="collapsed",
            )
            video_files[q["id"]] = vid

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Candidate Info ─────────────────────────────────────────────────────────
    st.markdown('<div class="q-section">', unsafe_allow_html=True)
    st.markdown('<div class="q-section-title">👤 Confirm Your Details</div>', unsafe_allow_html=True)
    ci1, ci2 = st.columns(2)
    with ci1:
        confirm_name = st.text_input("Full Name *", value=name)
    with ci2:
        confirm_email = st.text_input("Email Address *", value=email)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Consent & Submit ───────────────────────────────────────────────────────
    consent = st.checkbox("✅ I confirm that all my answers are truthful and I consent to the processing of my application data.")

    submitted = st.form_submit_button("🚀 Submit Interview Form", use_container_width=True, type="primary")

# ── Handle Submission ──────────────────────────────────────────────────────────
if submitted:
    errors = []

    if not consent:
        errors.append("Please check the consent checkbox before submitting.")
    if not confirm_name.strip():
        errors.append("Please enter your full name.")
    if not confirm_email.strip():
        errors.append("Please enter your email address.")

    # Validate text answers
    for q in skill_qs + project_qs:
        if not text_answers.get(q["id"], "").strip():
            errors.append(f"Please answer: '{q['question'][:60]}...'")

    # Validate videos
    for q in comm_qs:
        if video_files.get(q["id"]) is None:
            errors.append(f"Please upload a video for: '{q['question'][:50]}...'")

    if errors:
        for err in errors:
            st.error(f"❌ {err}")
    else:
        with st.spinner("Saving your responses..."):
            saved_video_paths = {}
            for q in comm_qs:
                vid = video_files.get(q["id"])
                if vid:
                    try:
                        path = storage.save_video(
                            candidate_id, q["id"], vid.getvalue(), vid.name
                        )
                        saved_video_paths[q["id"]] = path
                    except Exception as e:
                        st.error(f"Error saving video: {e}")

            # Add confirmed details to text responses
            text_answers["_name"] = confirm_name
            text_answers["_email"] = confirm_email

            storage.save_response(candidate_id, text_answers, saved_video_paths)

        st.markdown("""
        <div class="success-box">
            <div style="font-size:3.5rem;">🎉</div>
            <div style="font-size:1.4rem;font-weight:700;color:#34d399;margin:0.75rem 0;">
                Thank You! Form Submitted Successfully.
            </div>
            <div style="color:#94a3b8;font-size:0.95rem;max-width:400px;margin:0 auto;">
                Your responses have been recorded. The hiring team will review them and get back to you soon.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
