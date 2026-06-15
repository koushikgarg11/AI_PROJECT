"""
Page 3 — View Responses
Recruiters see all submitted candidate responses, read text answers, and play videos.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from backend import storage

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="View Responses | AI Hire",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d18 0%, #0a0a14 100%) !important;
    border-right: 1px solid rgba(124, 58, 237, 0.2);
}

.page-header {
    background: linear-gradient(135deg, #1a0533 0%, #0d1b3e 100%);
    border: 1px solid rgba(124, 58, 237, 0.3);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
}
.page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-subtitle { color: #64748b; font-size: 0.95rem; margin-top: 0.3rem; }

/* Candidate List Items */
.candidate-row {
    background: rgba(18, 18, 30, 0.85);
    border: 1px solid rgba(124, 58, 237, 0.15);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}
.candidate-row:hover {
    border-color: rgba(124, 58, 237, 0.45);
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.12);
}

.response-section {
    background: rgba(12, 12, 22, 0.9);
    border: 1px solid rgba(124, 58, 237, 0.12);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
}
.response-section-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #a78bfa;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(124,58,237,0.1);
}

.qa-block {
    margin-bottom: 1.25rem;
    padding: 1rem;
    background: rgba(124, 58, 237, 0.04);
    border-radius: 10px;
    border: 1px solid rgba(124,58,237,0.08);
}
.qa-question {
    color: #94a3b8;
    font-size: 0.83rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.qa-answer {
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.65;
    white-space: pre-wrap;
}

.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #334155;
}
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.2rem; color: #475569; font-weight: 600; }
.empty-desc { color: #334155; font-size: 0.88rem; margin-top: 0.5rem; }

.meta-pill {
    display: inline-block;
    background: rgba(30, 30, 50, 0.9);
    border: 1px solid rgba(124, 58, 237, 0.2);
    border-radius: 50px;
    padding: 0.25rem 0.8rem;
    color: #64748b;
    font-size: 0.78rem;
    margin-right: 0.5rem;
}

.score-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(109,40,217,0.1));
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 50px;
    padding: 0.3rem 0.9rem;
    color: #a78bfa;
    font-size: 0.82rem;
    font-weight: 600;
}

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
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35) !important;
}

.divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(124,58,237,0.3), transparent); margin: 1.5rem 0; }
.info-box {
    background: rgba(96, 165, 250, 0.08);
    border-left: 3px solid #60a5fa;
    border-radius: 0 10px 10px 0;
    padding: 0.85rem 1.1rem;
    color: #93c5fd;
    font-size: 0.88rem;
}

.stats-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-box {
    flex: 1;
    background: rgba(18, 18, 30, 0.8);
    border: 1px solid rgba(124, 58, 237, 0.2);
    border-radius: 12px;
    padding: 1.1rem;
    text-align: center;
}
.stat-num {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-lbl { color: #64748b; font-size: 0.78rem; margin-top: 0.15rem; }
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
    st.markdown("---")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">👁️ View Responses</div>
    <div class="page-subtitle">Review all submitted candidate interview responses, answers, and video recordings.</div>
</div>
""", unsafe_allow_html=True)

# ── Load Data ──────────────────────────────────────────────────────────────────
all_responses = storage.load_all_responses()
all_candidates = storage.load_all_candidates()

if not all_responses:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-title">No Responses Yet</div>
        <div class="empty-desc">Candidates haven't submitted their interview forms yet.<br>
        Share their unique form links from the Recruiter Dashboard.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Stats ─────────────────────────────────────────────────────────────────────
total_candidates = len(all_candidates)
total_responses = len(all_responses)
total_videos = sum(
    len(r.get("video_paths", {}))
    for r in all_responses.values()
)
latest = ""
if all_responses:
    times = [r.get("submitted_at", "") for r in all_responses.values()]
    latest = max(times) if times else ""
    try:
        latest = datetime.fromisoformat(latest).strftime("%d %b, %H:%M") if latest else "—"
    except Exception:
        latest = latest[:16] if latest else "—"

st.markdown(f"""
<div class="stats-row">
    <div class="stat-box">
        <div class="stat-num">{total_candidates}</div>
        <div class="stat-lbl">Forms Generated</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">{total_responses}</div>
        <div class="stat-lbl">Responses Received</div>
    </div>
    <div class="stat-box">
        <div class="stat-num">{total_videos}</div>
        <div class="stat-lbl">Videos Uploaded</div>
    </div>
    <div class="stat-box">
        <div class="stat-num" style="font-size:1.1rem;">{latest}</div>
        <div class="stat-lbl">Latest Submission</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Responses List ─────────────────────────────────────────────────────────────
st.markdown("### 📋 Candidate Submissions")

for candidate_id, response_data in all_responses.items():
    candidate = all_candidates.get(candidate_id, {})
    assessment = candidate.get("assessment", {})
    questions = candidate.get("questions", {})

    name = response_data.get("text_responses", {}).get("_name") or assessment.get("candidate_name", "Unknown")
    email = response_data.get("text_responses", {}).get("_email") or assessment.get("email", "—")
    score = assessment.get("match_score", "—")
    submitted_at = response_data.get("submitted_at", "")
    try:
        submitted_fmt = datetime.fromisoformat(submitted_at).strftime("%d %b %Y, %H:%M") if submitted_at else "—"
    except Exception:
        submitted_fmt = submitted_at[:16] if submitted_at else "—"

    video_count = len(response_data.get("video_paths", {}))
    skills = assessment.get("key_skills", [])

    with st.expander(f"👤 {name}  |  ID: {candidate_id}  |  Score: {score}%  |  📅 {submitted_fmt}", expanded=False):

        # Top meta row
        col_meta, col_btns = st.columns([4, 1])
        with col_meta:
            st.markdown(f"""
            <span class="meta-pill">📧 {email}</span>
            <span class="meta-pill">🎥 {video_count} video(s)</span>
            <span class="meta-pill">📄 {candidate.get('filename', '—')}</span>
            <span class="score-badge">🎯 Match: {score}%</span>
            """, unsafe_allow_html=True)

        with col_btns:
            # Export this candidate's data
            export_data = {
                "candidate_id": candidate_id,
                "name": name,
                "email": email,
                "match_score": score,
                "submitted_at": submitted_at,
                "text_responses": response_data.get("text_responses", {}),
            }
            st.download_button(
                "📥 Export",
                data=json.dumps(export_data, indent=2).encode("utf-8"),
                file_name=f"{candidate_id}_response.json",
                mime="application/json",
                key=f"export_{candidate_id}",
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # ── Skill Answers ──────────────────────────────────────────────────────
        skill_qs = questions.get("skill_questions", [])
        text_responses = response_data.get("text_responses", {})

        if skill_qs:
            st.markdown('<div class="response-section">', unsafe_allow_html=True)
            st.markdown('<div class="response-section-title">⚡ Technical Skills Answers</div>', unsafe_allow_html=True)
            for q in skill_qs:
                answer = text_responses.get(q["id"], "_(no answer)_")
                st.markdown(f"""
                <div class="qa-block">
                    <div class="qa-question">Q: {q["question"]}</div>
                    <div class="qa-answer">{answer if answer.strip() else "_(no answer provided)_"}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Project Answers ────────────────────────────────────────────────────
        project_qs = questions.get("project_questions", [])
        if project_qs:
            st.markdown('<div class="response-section">', unsafe_allow_html=True)
            st.markdown('<div class="response-section-title">🚀 Project Experience Answers</div>', unsafe_allow_html=True)
            for q in project_qs:
                answer = text_responses.get(q["id"], "")
                st.markdown(f"""
                <div class="qa-block">
                    <div class="qa-question">Q: {q["question"]}</div>
                    <div class="qa-answer">{answer if answer.strip() else "_(no answer provided)_"}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Video Responses ────────────────────────────────────────────────────
        comm_qs = questions.get("communication_questions", [])
        video_paths = response_data.get("video_paths", {})

        if comm_qs:
            st.markdown('<div class="response-section">', unsafe_allow_html=True)
            st.markdown('<div class="response-section-title">🎥 Communication Video Responses</div>', unsafe_allow_html=True)

            for i, q in enumerate(comm_qs, 1):
                st.markdown(f"""
                <div class="qa-block">
                    <div class="qa-question">Video Q{i}: {q["question"]}</div>
                </div>
                """, unsafe_allow_html=True)
                vid_path = video_paths.get(q["id"])
                if vid_path and storage.video_exists(vid_path):
                    path_obj = Path(vid_path)
                    try:
                        video_bytes = path_obj.read_bytes()
                        st.video(video_bytes)
                        size_mb = len(video_bytes) / (1024 * 1024)
                        st.caption(f"📁 {path_obj.name} — {size_mb:.1f} MB")
                        st.download_button(
                            f"⬇️ Download Video {i}",
                            data=video_bytes,
                            file_name=path_obj.name,
                            mime="video/mp4",
                            key=f"dl_vid_{candidate_id}_{q['id']}",
                        )
                    except Exception as e:
                        st.warning(f"Could not load video: {e}")
                else:
                    st.info("🎬 No video uploaded for this question.")

            st.markdown("</div>", unsafe_allow_html=True)

        # ── Assessment Summary ─────────────────────────────────────────────────
        if assessment:
            with st.expander("📊 Original AI Assessment"):
                a_col1, a_col2 = st.columns(2)
                with a_col1:
                    st.markdown("**Skills**")
                    for s in assessment.get("key_skills", []):
                        st.markdown(f"• {s}")
                    st.markdown("**Strengths**")
                    for s in assessment.get("strengths", []):
                        st.markdown(f"✓ {s}")
                with a_col2:
                    st.markdown("**Projects**")
                    for p in assessment.get("projects", []):
                        st.markdown(f"• {p}")
                    st.markdown("**Gaps**")
                    for g in assessment.get("gaps", []):
                        st.markdown(f"✗ {g}")
                st.markdown(f'<div class="info-box">{assessment.get("summary", "")}</div>', unsafe_allow_html=True)

# ── Full Export ────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
all_export = {
    cid: {
        "candidate": all_candidates.get(cid, {}).get("assessment", {}),
        "responses": rdata.get("text_responses", {}),
        "submitted_at": rdata.get("submitted_at", ""),
    }
    for cid, rdata in all_responses.items()
}
st.download_button(
    "📥 Export All Responses (JSON)",
    data=json.dumps(all_export, indent=2).encode("utf-8"),
    file_name="all_responses.json",
    mime="application/json",
)
