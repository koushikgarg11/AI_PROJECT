import streamlit as st
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.storage import load_all_submissions, load_shortlisted_candidates

st.set_page_config(page_title="Dashboard — TalentScreen AI", page_icon="📊", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .dash-header {
        background: linear-gradient(135deg, #0c1a2e, #1e3a5f);
        padding: 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
    }
    .dash-header h2 { font-family: 'Space Grotesk', sans-serif; color: #bfdbfe; margin: 0; }
    .dash-header p { color: #60a5fa; margin: 0.3rem 0 0; }

    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .metric-card .num { font-size: 2.2rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; }
    .metric-card .label { color: #64748b; font-size: 0.82rem; margin-top: 0.2rem; }

    .submission-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1rem;
    }

    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .status-submitted { background: #0c2340; color: #60a5fa; }
    .status-pending { background: #1a1207; color: #fbbf24; }

    .answer-box {
        background: #1e293b;
        border-radius: 8px;
        padding: 0.8rem;
        margin-top: 0.4rem;
        color: #94a3b8;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    .video-indicator {
        background: #2d1b69;
        border: 1px solid #4f46e5;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        color: #c4b5fd;
        font-size: 0.85rem;
        margin-top: 0.4rem;
    }

    [data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e293b; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="dash-header">
    <h2>📊 HR Dashboard</h2>
    <p>Overview of all candidates, shortlists, and assessment submissions</p>
</div>
""", unsafe_allow_html=True)

# Load data
all_candidates = load_shortlisted_candidates()
all_submissions = load_all_submissions()

shortlisted = [c for c in all_candidates if c.get("shortlisted")]
submitted_ids = {s.get("candidate_id") for s in all_submissions}
pending = [c for c in shortlisted if c.get("candidate_id") not in submitted_ids]

# Metrics
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="num" style="color:#60a5fa">{len(all_candidates)}</div>
        <div class="label">Total Screened</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="num" style="color:#34d399">{len(shortlisted)}</div>
        <div class="label">Shortlisted</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="num" style="color:#a78bfa">{len(all_submissions)}</div>
        <div class="label">Forms Submitted</div>
    </div>""", unsafe_allow_html=True)
with c4:
    rate = int((len(all_submissions) / len(shortlisted)) * 100) if shortlisted else 0
    st.markdown(f"""<div class="metric-card">
        <div class="num" style="color:#fb923c">{rate}%</div>
        <div class="label">Response Rate</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["✅ Submitted Assessments", "⏳ Pending Candidates", "📋 All Screened"])

with tab1:
    if not all_submissions:
        st.info("No assessments submitted yet.")
    else:
        st.markdown(f"**{len(all_submissions)} assessment(s) received**")
        for sub in sorted(all_submissions, key=lambda x: x.get("submitted_at", ""), reverse=True):
            with st.expander(f"📄 {sub.get('candidate_name', 'Unknown')} — submitted {sub.get('submitted_at', '')}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Email:** {sub.get('email', 'N/A')}")
                    st.markdown(f"**Role:** {sub.get('job_title', 'N/A')}")
                with col2:
                    st.markdown(f'<span class="status-badge status-submitted">✅ Submitted</span>', unsafe_allow_html=True)

                questions = sub.get("questions", [])
                answers = sub.get("answers", {})

                st.markdown("---")
                st.markdown("**Assessment Responses:**")

                for i, q in enumerate(questions):
                    q_type = q.get("type", "skill")
                    q_text = q.get("question", "")
                    q_id = f"q_{i}"
                    ans_data = answers.get(q_id, {})

                    type_icon = "🎥" if q_type == "video" else ("📁" if q_type == "project" else "⚡")
                    st.markdown(f"**{type_icon} Q{i+1}:** {q_text}")

                    if q_type == "video":
                        video_path = ans_data.get("video_path", "")
                        note = ans_data.get("note", "")
                        video_name = ans_data.get("video_name", "")

                        if video_path and os.path.exists(video_path):
                            st.markdown(f'<div class="video-indicator">🎥 Video submitted: <strong>{video_name}</strong></div>', unsafe_allow_html=True)
                            with open(video_path, "rb") as vf:
                                st.video(vf.read())
                        elif video_name:
                            st.markdown(f'<div class="video-indicator">🎥 Video: {video_name} (file processing)</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="video-indicator">⚠️ No video uploaded</div>', unsafe_allow_html=True)

                        if note:
                            st.markdown(f'<div class="answer-box"><em>Candidate note:</em> {note}</div>', unsafe_allow_html=True)
                    else:
                        answer_text = ans_data.get("answer", "No response provided")
                        st.markdown(f'<div class="answer-box">{answer_text}</div>', unsafe_allow_html=True)

                    st.markdown("")

with tab2:
    if not pending:
        st.success("All shortlisted candidates have submitted their assessments!")
    else:
        st.markdown(f"**{len(pending)} candidate(s) yet to submit**")
        for c in pending:
            st.markdown(f"""
            <div class="submission-card">
                <strong style="color:#e2e8f0">{c.get('name', 'Unknown')}</strong>
                <span class="status-badge status-pending" style="float:right">⏳ Pending</span><br>
                <span style="color:#94a3b8; font-size:0.85rem">📧 {c.get('email', 'N/A')} | Score: {c.get('score', 0)}%</span>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    if not all_candidates:
        st.info("No resumes screened yet. Go to the HR Portal to upload resumes.")
    else:
        shortlisted_ids = {c.get("candidate_id") for c in shortlisted}
        for c in sorted(all_candidates, key=lambda x: x.get("score", 0), reverse=True):
            is_short = c.get("shortlisted", False)
            color = "#34d399" if is_short else "#f87171"
            badge = "✅ Shortlisted" if is_short else "❌ Rejected"
            bg = "#0d2b1f" if is_short else "#2b0d0d"

            st.markdown(f"""
            <div class="submission-card" style="border-left: 4px solid {color}">
                <strong style="color:#e2e8f0">{c.get('name', 'Unknown')}</strong>
                <span style="float:right; color:{color}; font-size:0.85rem">{badge} | {c.get('score', 0)}%</span><br>
                <span style="color:#94a3b8; font-size:0.82rem">{c.get('summary', '')}</span>
            </div>
            """, unsafe_allow_html=True)
