import streamlit as st
import os
import json
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_screener import generate_candidate_questions
from utils.storage import load_shortlisted_candidates, save_submission, submission_exists

st.set_page_config(page_title="Candidate Assessment — TalentScreen AI", page_icon="📝", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .form-header {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        padding: 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
    }
    .form-header h2 { font-family: 'Space Grotesk', sans-serif; color: #e0e7ff; margin: 0; }
    .form-header p { color: #a5b4fc; margin: 0.3rem 0 0; }

    .question-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1rem;
    }

    .question-label {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }

    .question-type {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }

    .type-company { background: #1c1a0e; color: #fbbf24; }
    .type-skill { background: #1e3a5f; color: #60a5fa; }
    .type-project { background: #1a2e1a; color: #86efac; }
    .type-video { background: #3b1f5e; color: #d8b4fe; }

    .video-upload-area {
        background: #1e1b4b;
        border: 2px dashed #4f46e5;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 0.5rem;
    }

    .progress-bar-custom {
        background: #1e293b;
        border-radius: 10px;
        height: 8px;
        margin-bottom: 1.5rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        width: 100%;
        padding: 0.7rem;
    }

    .stTextArea textarea {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] * { color: #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# Get candidate ID from query params
params = st.query_params
candidate_id = params.get("candidate_id", "")

st.markdown("""
<div class="form-header">
    <h2>📝 Candidate Assessment Form</h2>
    <p>Answer the questions below honestly — they're tailored to your profile</p>
</div>
""", unsafe_allow_html=True)

# Load candidates
candidates = load_shortlisted_candidates()
shortlisted = [c for c in candidates if c.get("shortlisted")]

# Candidate lookup
candidate = None
if candidate_id:
    for c in shortlisted:
        if c.get("candidate_id") == candidate_id:
            candidate = c
            break

if not shortlisted:
    st.warning("⚠️ No shortlisted candidates found yet. HR needs to screen resumes first.")
    st.stop()

# If no candidate_id in URL, let them select (demo mode)
if not candidate:
    st.info("🔍 Select your name to access your personalized assessment form:")
    name_options = {c.get("name", "Unknown"): c for c in shortlisted}
    selected_name = st.selectbox("Your Name", ["— Select —"] + list(name_options.keys()))
    if selected_name == "— Select —":
        st.stop()
    candidate = name_options[selected_name]
    candidate_id = candidate.get("candidate_id", "")

# Check already submitted
if submission_exists(candidate_id):
    st.success("✅ You have already submitted your assessment. Thank you!")
    st.info("Our HR team will review your responses and get back to you shortly.")
    st.stop()

st.markdown(f"### Welcome, {candidate.get('name', 'Candidate')}! 👋")
st.markdown(f"*Role: **{candidate.get('job_title', 'Position')}** at {candidate.get('company', '')}*")
st.markdown("---")

# Generate questions (cache per candidate per version — bump version to force regeneration)
QUESTIONS_VERSION = "v3"
cache_key = f"questions_{candidate_id}_{QUESTIONS_VERSION}"
if cache_key not in st.session_state:
    with st.spinner("🤖 AI is generating personalized questions based on your resume..."):
        questions = generate_candidate_questions(candidate)
        st.session_state[cache_key] = questions
else:
    questions = st.session_state[cache_key]

if not questions:
    st.error("Could not generate questions. Please try again later.")
    st.stop()

# Progress tracker
total_q = len(questions)
answered = 0

st.markdown(f"**{total_q} questions** — including 2 video response questions")

answers = {}
video_files = {}

with st.form("assessment_form", clear_on_submit=False):
    for i, q in enumerate(questions):
        q_type = q.get("type", "skill")
        q_text = q.get("question", "")
        q_id = f"q_{i}"

        # Type badge styling
        if q_type == "video":
            badge_class = "type-video"
            badge_label = "🎥 Video Required"
        elif q_type == "project":
            badge_class = "type-project"
            badge_label = "📁 Project"
        elif q_type == "company":
            badge_class = "type-company"
            badge_label = "🏢 Company Fit"
        else:
            badge_class = "type-skill"
            badge_label = "⚡ Skill"

        st.markdown(f"""
        <div class="question-card">
            <span class="question-type {badge_class}">{badge_label}</span>
            <div class="question-label">Q{i+1}. {q_text}</div>
        </div>
        """, unsafe_allow_html=True)

        if q_type == "video":
            st.markdown(f"""
            <div class="video-upload-area">
                <p style="color:#d8b4fe; font-size:0.9rem; margin:0">🎥 Record a video (max 5 min) answering this question</p>
                <p style="color:#94a3b8; font-size:0.8rem">Accepted: MP4, MOV, AVI, WebM</p>
            </div>
            """, unsafe_allow_html=True)
            video = st.file_uploader(
                f"Upload video for Q{i+1}",
                type=["mp4", "mov", "avi", "webm"],
                key=f"video_{q_id}",
                label_visibility="collapsed"
            )
            if video:
                video_files[q_id] = video
                st.success(f"✅ Video uploaded: {video.name}")
            # Also allow text note
            note = st.text_area(
                f"Optional written note for Q{i+1} (summary of your video)",
                key=f"note_{q_id}",
                height=60,
                placeholder="Briefly describe what you covered in your video..."
            )
            answers[q_id] = {"type": "video", "note": note, "video_name": video.name if video else ""}
        else:
            answer = st.text_area(
                f"Your answer for Q{i+1}",
                key=f"answer_{q_id}",
                height=100,
                placeholder="Write your detailed answer here...",
                label_visibility="collapsed"
            )
            answers[q_id] = {"type": q_type, "answer": answer}

        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    # Consent
    consent = st.checkbox("✅ I confirm that all information provided is accurate and I consent to this assessment being reviewed by the hiring team.")

    submitted = st.form_submit_button("🚀 Submit Assessment")

    if submitted:
        if not consent:
            st.error("Please confirm the consent checkbox before submitting.")
        else:
            # Save videos to disk
            submission_dir = os.path.join("submissions", candidate_id)
            os.makedirs(submission_dir, exist_ok=True)

            video_paths = {}
            for q_id, vf in video_files.items():
                video_path = os.path.join(submission_dir, vf.name)
                with open(video_path, "wb") as f:
                    f.write(vf.read())
                video_paths[q_id] = video_path

            # Merge video paths into answers
            for q_id in answers:
                if answers[q_id].get("type") == "video":
                    answers[q_id]["video_path"] = video_paths.get(q_id, "")

            submission = {
                "candidate_id": candidate_id,
                "candidate_name": candidate.get("name"),
                "email": candidate.get("email"),
                "job_title": candidate.get("job_title"),
                "questions": questions,
                "answers": answers,
                "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            save_submission(submission)
            st.success("🎉 Assessment submitted successfully! HR will be in touch soon.")
            st.balloons()
