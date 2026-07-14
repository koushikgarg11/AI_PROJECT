import streamlit as st
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ai_screener import screen_resumes, extract_text_from_file
from utils.storage import save_job_criteria, load_job_criteria, save_shortlisted_candidates

st.set_page_config(page_title="HR Portal — TalentScreen AI", page_icon="🏢", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .page-header {
        background: linear-gradient(135deg, #064e3b, #065f46);
        padding: 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
    }
    .page-header h2 { font-family: 'Space Grotesk', sans-serif; color: #d1fae5; margin: 0; }
    .page-header p { color: #6ee7b7; margin: 0.3rem 0 0; }

    .criteria-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .result-card {
        background: #0f172a;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #10b981;
    }

    .result-card.rejected {
        border-left-color: #ef4444;
    }

    .score-badge {
        display: inline-block;
        background: #064e3b;
        color: #6ee7b7;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .score-badge.low {
        background: #450a0a;
        color: #fca5a5;
    }

    .stButton > button {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }

    [data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e293b; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <h2>🏢 HR Portal</h2>
    <p>Set your hiring criteria, upload resumes, and let AI do the screening</p>
</div>
""", unsafe_allow_html=True)

# Load existing criteria
existing = load_job_criteria()

tab1, tab2 = st.tabs(["⚙️ Job Criteria & Upload", "📋 Screening Results"])

with tab1:
    st.markdown("#### Job Details")
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title", value=existing.get("job_title", ""), placeholder="e.g. Senior Python Developer")
        company = st.text_input("Company Name", value=existing.get("company", ""), placeholder="e.g. TechCorp Inc.")
        experience_min = st.number_input("Minimum Years of Experience", min_value=0, max_value=30, value=existing.get("experience_min", 2))
    with col2:
        department = st.text_input("Department", value=existing.get("department", ""), placeholder="e.g. Engineering")
        location = st.text_input("Location", value=existing.get("location", ""), placeholder="e.g. Remote / Delhi")
        experience_max = st.number_input("Maximum Years of Experience", min_value=0, max_value=30, value=existing.get("experience_max", 8))

    st.markdown("#### Required Skills")
    col3, col4 = st.columns(2)
    with col3:
        must_have_skills = st.text_area(
            "Must-Have Skills (one per line)",
            value="\n".join(existing.get("must_have_skills", [])),
            placeholder="Python\nSQL\nMachine Learning\nREST APIs",
            height=120
        )
    with col4:
        nice_to_have_skills = st.text_area(
            "Nice-to-Have Skills (one per line)",
            value="\n".join(existing.get("nice_to_have_skills", [])),
            placeholder="Docker\nKubernetes\nAWS\nFastAPI",
            height=120
        )

    st.markdown("#### Qualifications")
    col5, col6 = st.columns(2)
    with col5:
        education = st.selectbox(
            "Minimum Education",
            ["Any", "High School", "Diploma", "Bachelor's", "Master's", "PhD"],
            index=["Any", "High School", "Diploma", "Bachelor's", "Master's", "PhD"].index(existing.get("education", "Bachelor's"))
        )
    with col6:
        shortlist_threshold = st.slider("Shortlist Score Threshold (%)", 40, 90, existing.get("shortlist_threshold", 65),
                                         help="Candidates scoring above this are shortlisted")

    additional_criteria = st.text_area(
        "Additional Criteria / Notes for AI",
        value=existing.get("additional_criteria", ""),
        placeholder="e.g. Must have experience with fintech projects, prior startup experience preferred, strong communication skills needed",
        height=80
    )

    if st.button("💾 Save Job Criteria"):
        criteria = {
            "job_title": job_title,
            "company": company,
            "department": department,
            "location": location,
            "experience_min": experience_min,
            "experience_max": experience_max,
            "must_have_skills": [s.strip() for s in must_have_skills.split("\n") if s.strip()],
            "nice_to_have_skills": [s.strip() for s in nice_to_have_skills.split("\n") if s.strip()],
            "education": education,
            "shortlist_threshold": shortlist_threshold,
            "additional_criteria": additional_criteria,
        }
        save_job_criteria(criteria)
        st.success("✅ Criteria saved successfully!")

    st.markdown("---")
    st.markdown("#### Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload resume files (PDF or DOCX)",
        accept_multiple_files=True,
        type=["pdf", "docx"],
        help="Upload up to 50 resumes at once"
    )

    if uploaded_files:
        st.info(f"📎 {len(uploaded_files)} resume(s) uploaded. Ready to screen.")

        if st.button(f"🤖 Screen {len(uploaded_files)} Resume(s) with AI"):
            criteria = load_job_criteria()
            if not criteria.get("job_title"):
                st.error("Please save your job criteria first!")
            else:
                with st.spinner("🔍 AI is reading and scoring all resumes..."):
                    # Save uploaded files temporarily
                    temp_files = []
                    upload_dir = "uploads"
                    os.makedirs(upload_dir, exist_ok=True)
                    for f in uploaded_files:
                        path = os.path.join(upload_dir, f.name)
                        with open(path, "wb") as out:
                            out.write(f.read())
                        temp_files.append(path)

                    results = screen_resumes(temp_files, criteria)
                    save_shortlisted_candidates(results)
                    st.session_state["screening_results"] = results
                    st.success(f"✅ Screening complete! {sum(1 for r in results if r.get('shortlisted'))} candidates shortlisted.")
                    st.rerun()

with tab2:
    results = st.session_state.get("screening_results", [])
    if not results:
        # Try loading from disk
        from utils.storage import load_shortlisted_candidates
        results = load_shortlisted_candidates()

    if not results:
        st.info("No screening results yet. Upload and screen resumes in the first tab.")
    else:
        shortlisted = [r for r in results if r.get("shortlisted")]
        rejected = [r for r in results if not r.get("shortlisted")]

        st.markdown(f"#### Results Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Screened", len(results))
        m2.metric("✅ Shortlisted", len(shortlisted))
        m3.metric("❌ Not Shortlisted", len(rejected))

        st.markdown("---")
        st.markdown("#### ✅ Shortlisted Candidates")
        if not shortlisted:
            st.warning("No candidates met the threshold. Consider lowering the score threshold.")
        for r in sorted(shortlisted, key=lambda x: x.get("score", 0), reverse=True):
            score = r.get("score", 0)
            st.markdown(f"""
            <div class="result-card">
                <strong style="color:#d1fae5; font-size:1rem">{r.get('name', 'Unknown')}</strong>
                <span class="score-badge" style="float:right">Score: {score}%</span><br>
                <span style="color:#6ee7b7; font-size:0.85rem">📧 {r.get('email', 'N/A')} | 📁 {r.get('filename', '')}</span><br>
                <span style="color:#94a3b8; font-size:0.82rem; margin-top:0.3rem; display:block">{r.get('summary', '')}</span>
                <details style="margin-top:0.5rem">
                    <summary style="color:#6ee7b7; cursor:pointer; font-size:0.82rem">View AI reasoning</summary>
                    <p style="color:#94a3b8; font-size:0.8rem; margin-top:0.4rem">{r.get('reasoning', '')}</p>
                </details>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ❌ Not Shortlisted")
        for r in sorted(rejected, key=lambda x: x.get("score", 0), reverse=True):
            score = r.get("score", 0)
            st.markdown(f"""
            <div class="result-card rejected">
                <strong style="color:#fee2e2; font-size:0.95rem">{r.get('name', 'Unknown')}</strong>
                <span class="score-badge low" style="float:right">Score: {score}%</span><br>
                <span style="color:#fca5a5; font-size:0.82rem">📁 {r.get('filename', '')}</span><br>
                <span style="color:#94a3b8; font-size:0.8rem; display:block; margin-top:0.3rem">{r.get('reasoning', '')}</span>
            </div>
            """, unsafe_allow_html=True)

        if shortlisted:
            st.markdown("---")
            st.markdown("#### 🔗 Candidate Assessment Links")
            st.info("Share these unique links with shortlisted candidates to fill out their assessment form.")
            for r in shortlisted:
                cid = r.get("candidate_id", "")
                link = f"?candidate_id={cid}"
                st.code(f"Candidate Assessment Form: /Candidate_Form{link}", language=None)
