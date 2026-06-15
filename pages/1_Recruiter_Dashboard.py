"""
Page 1 — Recruiter Dashboard
Define job criteria, upload resumes, run AI shortlisting, generate candidate form links.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from backend.gemini_client import initialize_gemini
from backend.resume_parser import extract_text
from backend.shortlister import shortlist_resume
from backend.question_generator import generate_interview_questions
from backend import storage

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Recruiter Dashboard | AI Hire",
    page_icon="📋",
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
    margin: 0;
}
.page-subtitle { color: #64748b; font-size: 0.95rem; margin-top: 0.4rem; }

.section-card {
    background: rgba(18, 18, 30, 0.8);
    border: 1px solid rgba(124, 58, 237, 0.2);
    border-radius: 14px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}
.section-heading {
    font-size: 1rem;
    font-weight: 600;
    color: #a78bfa;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Candidate result card */
.candidate-card {
    background: rgba(12, 12, 22, 0.9);
    border: 1px solid rgba(124, 58, 237, 0.15);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.candidate-card:hover {
    border-color: rgba(124, 58, 237, 0.4);
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.1);
}
.candidate-card.shortlisted {
    border-left: 3px solid #10b981;
}
.candidate-card.rejected {
    border-left: 3px solid rgba(239, 68, 68, 0.5);
}

.score-ring {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    font-size: 1.1rem;
    font-weight: 700;
    border: 3px solid;
}
.score-high { border-color: #10b981; color: #34d399; background: rgba(16, 185, 129, 0.1); }
.score-mid  { border-color: #f59e0b; color: #fbbf24; background: rgba(245, 158, 11, 0.1); }
.score-low  { border-color: #ef4444; color: #f87171; background: rgba(239, 68, 68, 0.1); }

.skill-tag {
    display: inline-block;
    background: rgba(124, 58, 237, 0.15);
    border: 1px solid rgba(124, 58, 237, 0.3);
    color: #a78bfa;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 0.15rem;
}
.strength-tag {
    display: inline-block;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #34d399;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.78rem;
    margin: 0.15rem;
}
.gap-tag {
    display: inline-block;
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: #f87171;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.78rem;
    margin: 0.15rem;
}

.form-link-box {
    background: rgba(96, 165, 250, 0.06);
    border: 1px dashed rgba(96, 165, 250, 0.3);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    color: #60a5fa;
    word-break: break-all;
    margin-top: 0.5rem;
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
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
}

.stats-bar {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-item {
    flex: 1;
    background: rgba(18, 18, 30, 0.8);
    border: 1px solid rgba(124, 58, 237, 0.2);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
}
.stat-number {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-label { color: #64748b; font-size: 0.82rem; margin-top: 0.2rem; }

.divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(124,58,237,0.3), transparent); margin: 1.5rem 0; }
.info-box {
    background: rgba(96, 165, 250, 0.08);
    border-left: 3px solid #60a5fa;
    border-radius: 0 10px 10px 0;
    padding: 0.85rem 1.1rem;
    color: #93c5fd;
    font-size: 0.88rem;
    margin: 0.75rem 0;
}
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
    if st.session_state.get("gemini_ready"):
        st.markdown('<span style="color:#34d399;font-size:0.85rem;">✅ Gemini Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#fbbf24;font-size:0.85rem;">⚠️ API Key Needed</span>', unsafe_allow_html=True)


# ── Auth Guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("gemini_ready"):
    st.warning("⚠️ Please go to the **Home** page and connect your Gemini API key first.")
    st.stop()

model = st.session_state["gemini_model"]

# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">📋 Recruiter Dashboard</div>
    <div class="page-subtitle">Define criteria → Upload resumes → AI shortlists candidates → Generate interview forms</div>
</div>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = []
if "criteria" not in st.session_state:
    st.session_state.criteria = storage.load_criteria()
if "generated_ids" not in st.session_state:
    st.session_state.generated_ids = {}  # filename -> candidate_id

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Job Criteria
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-heading">🎯 Step 1 — Define Job Criteria</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    job_title = st.text_input("Job Title *", placeholder="e.g. Senior Python Developer", value=st.session_state.criteria.get("job_title", ""))
    skills_input = st.text_input(
        "Required Skills (comma-separated) *",
        placeholder="e.g. Python, Django, REST APIs, PostgreSQL",
        value=", ".join(st.session_state.criteria.get("skills", [])),
    )
    education = st.selectbox(
        "Minimum Education",
        ["Any", "Bachelor's Degree", "Master's Degree", "PhD"],
        index=["Any", "Bachelor's Degree", "Master's Degree", "PhD"].index(
            st.session_state.criteria.get("education", "Any")
        ),
    )

with col2:
    min_exp = st.slider(
        "Minimum Experience (years)",
        min_value=0, max_value=20, step=1,
        value=st.session_state.criteria.get("min_experience", 2),
    )
    shortlist_threshold = st.slider(
        "Shortlist Score Threshold (%)",
        min_value=40, max_value=90, step=5, value=60,
        help="Candidates scoring at or above this threshold will be shortlisted.",
    )
    additional = st.text_area(
        "Additional Requirements",
        placeholder="e.g. Must have experience with microservices, cloud deployment...",
        value=st.session_state.criteria.get("additional", ""),
        height=100,
    )

save_col, _ = st.columns([1, 4])
with save_col:
    if st.button("💾 Save Criteria", use_container_width=True):
        criteria = {
            "job_title": job_title,
            "skills": [s.strip() for s in skills_input.split(",") if s.strip()],
            "min_experience": min_exp,
            "education": education,
            "additional": additional,
            "threshold": shortlist_threshold,
        }
        storage.save_criteria(criteria)
        st.session_state.criteria = criteria
        st.success("✅ Criteria saved!")

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Resume Upload
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-heading">📄 Step 2 — Upload Candidate Resumes HERE ⬇️</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(124, 58, 237, 0.08); border: 2px dashed rgba(124, 58, 237, 0.4);
border-radius: 14px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; text-align: center;">
    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
    <div style="color: #a78bfa; font-weight: 600; font-size: 1rem;">Drop or Browse Resume Files Below</div>
    <div style="color: #64748b; font-size: 0.85rem; margin-top: 0.3rem;">
        Supports <strong>PDF</strong>, <strong>DOCX</strong>, and <strong>TXT</strong> formats &nbsp;|&nbsp;
        You can upload <strong>multiple files at once</strong>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Upload Resume Files (PDF / DOCX / TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

if uploaded_files:
    st.markdown(f"**✅ {len(uploaded_files)} resume(s) ready for analysis:**")
    for f in uploaded_files:
        size_kb = len(f.getvalue()) / 1024
        st.markdown(f"- 📄 `{f.name}` — {size_kb:.1f} KB")
else:
    st.info("👆 Click 'Browse files' or drag and drop resumes above, then click **Run AI Shortlisting** below.")

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Run Shortlisting
# ══════════════════════════════════════════════════════════════════════════════
run_col, clear_col, _ = st.columns([2, 1, 4])
with run_col:
    run_btn = st.button("🚀 Run AI Shortlisting", use_container_width=True, type="primary")
with clear_col:
    if st.button("🗑️ Clear Results", use_container_width=True):
        st.session_state.results = []
        st.session_state.generated_ids = {}
        st.rerun()

if run_btn:
    if not uploaded_files:
        st.warning("Please upload at least one resume.")
    elif not job_title.strip():
        st.warning("Please enter a Job Title before shortlisting.")
    else:
        criteria = {
            "job_title": job_title,
            "skills": [s.strip() for s in skills_input.split(",") if s.strip()],
            "min_experience": min_exp,
            "education": education,
            "additional": additional,
            "threshold": shortlist_threshold,
        }
        storage.save_criteria(criteria)
        st.session_state.criteria = criteria

        results = []
        total_files = len(uploaded_files)
        progress = st.progress(0, text="Analyzing resumes...")
        status_container = st.empty()

        # ── Phase 1: Score every resume ───────────────────────────────────────
        for i, uf in enumerate(uploaded_files):
            status_container.markdown(f"🔍 **[{i+1}/{total_files}]** Scoring **{uf.name}**...")
            try:
                text = extract_text(uf.getvalue(), uf.name)
                if len(text.strip()) < 50:
                    st.warning(f"⚠️ `{uf.name}` appears to have very little text. Skipping.")
                    continue
                pref_model = st.session_state.get("preferred_model", "gemini-2.5-flash")
                assessment = shortlist_resume(model, text, criteria, preferred_model=pref_model)
                assessment["shortlisted"] = assessment["match_score"] >= shortlist_threshold
                assessment["_resume_text"] = text
                assessment["_filename"] = uf.name
                results.append(assessment)
            except Exception as e:
                st.error(f"❌ Error processing `{uf.name}`: {e}")
            progress.progress((i + 1) / (total_files * 2), text=f"Scored {i+1}/{total_files} resumes...")

        # ── Phase 2: Auto-generate personalized questions for shortlisted ─────
        shortlisted = [r for r in results if r.get("shortlisted")]
        for j, r in enumerate(shortlisted):
            filename = r.get("_filename", f"candidate_{j}")
            status_container.markdown(
                f"🧠 **[{j+1}/{len(shortlisted)}]** Generating personalized questions for **{r.get('candidate_name', filename)}**..."
            )
            try:
                pref_model = st.session_state.get("preferred_model", "gemini-2.5-flash")
                questions = generate_interview_questions(
                    model, r, r.get("_resume_text", ""),
                    preferred_model=pref_model,
                )
                c_id = storage.generate_candidate_id()
                candidate_data = {
                    "id": c_id,
                    "assessment": {k: v for k, v in r.items() if not k.startswith("_")},
                    "questions": questions,
                    "filename": filename,
                }
                storage.save_candidate(c_id, candidate_data)
                st.session_state.generated_ids[filename] = c_id
            except Exception as e:
                st.warning(f"⚠️ Could not generate questions for `{filename}`: {e}")
            progress.progress(
                (total_files + j + 1) / (total_files * 2),
                text=f"Generated questions {j+1}/{len(shortlisted)}..."
            )

        status_container.empty()
        progress.empty()
        st.session_state.results = results

        if results:
            shortlisted_count = sum(1 for r in results if r.get("shortlisted"))
            st.success(
                f"✅ Done! **{shortlisted_count} shortlisted** out of {len(results)} candidates. "
                f"Personalized interview forms auto-generated for all shortlisted candidates."
            )
        else:
            st.warning("No valid resumes could be processed.")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Results
# ══════════════════════════════════════════════════════════════════════════════
results = st.session_state.get("results", [])

if results:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Shortlisting Results")

    # Stats bar
    total = len(results)
    shortlisted = sum(1 for r in results if r.get("shortlisted"))
    avg_score = int(sum(r.get("match_score", 0) for r in results) / total) if total else 0
    forms_generated = len(st.session_state.get("generated_ids", {}))

    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-number">{total}</div>
            <div class="stat-label">Total Analyzed</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{shortlisted}</div>
            <div class="stat-label">Shortlisted</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{total - shortlisted}</div>
            <div class="stat-label">Rejected</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{avg_score}%</div>
            <div class="stat-label">Avg Match Score</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{forms_generated}</div>
            <div class="stat-label">Forms Generated</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter tabs
    tab_all, tab_shortlisted, tab_rejected = st.tabs([
        f"All ({total})",
        f"✅ Shortlisted ({shortlisted})",
        f"❌ Rejected ({total - shortlisted})",
    ])

    # ── Determine app base URL (works locally and on Streamlit Cloud) ─────────
    try:
        _app_url = st.secrets.get("APP_URL", "").rstrip("/")
    except Exception:
        _app_url = ""
    if not _app_url:
        # Auto-detect from Streamlit context headers when available
        try:
            _host = st.context.headers.get("host", "localhost:8501")
            _proto = "https" if ".streamlit.app" in _host else "http"
            _app_url = f"{_proto}://{_host}"
        except Exception:
            _app_url = "http://localhost:8501"

    def render_candidates(candidates_list, tab_prefix="all", show_form_gen=True):
        if not candidates_list:
            st.info("No candidates in this category.")
            return

        for idx, r in enumerate(sorted(candidates_list, key=lambda x: x.get("match_score", 0), reverse=True)):
            score = r.get("match_score", 0)
            is_shortlisted = r.get("shortlisted", False)
            card_class = "shortlisted" if is_shortlisted else "rejected"
            filename = r.get("_filename", f"candidate_{idx}")
            # Unique key per tab + filename + position — prevents duplicate key crash
            safe_fname = filename.replace(".", "_").replace(" ", "_")
            uid = f"{tab_prefix}_{safe_fname}_{idx}"

            if score >= 70:
                score_class = "score-high"
            elif score >= 50:
                score_class = "score-mid"
            else:
                score_class = "score-low"

            status_icon = "✅" if is_shortlisted else "❌"
            status_label = "Shortlisted" if is_shortlisted else "Not Shortlisted"

            with st.container():
                st.markdown(f'<div class="candidate-card {card_class}">', unsafe_allow_html=True)

                col_score, col_info, col_action = st.columns([1, 5, 2])

                with col_score:
                    st.markdown(f'<div class="score-ring {score_class}">{score}%</div>', unsafe_allow_html=True)

                with col_info:
                    name = r.get("candidate_name", "Unknown")
                    email = r.get("email", "—")
                    exp = r.get("years_experience", 0)
                    edu = r.get("education", "—")

                    st.markdown(f"""
                    <div style="margin-bottom:0.5rem;">
                        <strong style="color:#e2e8f0;font-size:1.05rem;">{name}</strong>
                        &nbsp;<span style="color:#64748b;font-size:0.82rem;">{status_icon} {status_label}</span>
                    </div>
                    <div style="color:#64748b;font-size:0.82rem;margin-bottom:0.6rem;">
                        📧 {email} &nbsp;|&nbsp; 💼 {exp} yrs exp &nbsp;|&nbsp; 🎓 {edu}
                        &nbsp;|&nbsp; 📄 {filename}
                    </div>
                    """, unsafe_allow_html=True)

                    skills_html = " ".join(
                        f'<span class="skill-tag">{s}</span>'
                        for s in r.get("key_skills", [])[:6]
                    )
                    if skills_html:
                        st.markdown(f'<div>{skills_html}</div>', unsafe_allow_html=True)

                with col_action:
                    c_id_for_this = st.session_state.get("generated_ids", {}).get(filename)
                    if is_shortlisted and show_form_gen:
                        if c_id_for_this:
                            st.markdown(
                                '<span style="color:#34d399;font-size:0.82rem;">✅ Form Ready</span>',
                                unsafe_allow_html=True
                            )
                        else:
                            # Manual re-generate button (fallback if auto-gen failed)
                            if st.button("🔄 Regenerate Form", key=f"regen_{uid}", use_container_width=True):
                                with st.spinner("Generating personalized interview form..."):
                                    try:
                                        pref_model = st.session_state.get("preferred_model", "gemini-2.5-flash")
                                        questions = generate_interview_questions(
                                            model, r, r.get("_resume_text", ""),
                                            preferred_model=pref_model,
                                        )
                                        c_id = storage.generate_candidate_id()
                                        candidate_data = {
                                            "id": c_id,
                                            "assessment": {k: v for k, v in r.items() if not k.startswith("_")},
                                            "questions": questions,
                                            "filename": filename,
                                        }
                                        storage.save_candidate(c_id, candidate_data)
                                        st.session_state.generated_ids[filename] = c_id
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")

                # Show form link if generated
                c_id_for_this = st.session_state.get("generated_ids", {}).get(filename)
                if c_id_for_this:
                    form_url = f"{_app_url}/Candidate_Form?candidate_id={c_id_for_this}"
                    st.markdown(f"""
                    <div class="form-link-box">
                        🔗 Form Link for <strong>{r.get('candidate_name', 'candidate')}</strong>:<br>
                        {form_url}
                        <br><span style="color:#64748b;font-size:0.75rem;">Candidate ID: {c_id_for_this}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(form_url, language=None)

                # Expandable details — unique key per tab prevents duplicate expander crash
                with st.expander("📖 View Full Assessment", expanded=False):
                    d_col1, d_col2 = st.columns(2)
                    with d_col1:
                        st.markdown("**💪 Strengths**")
                        for s in r.get("strengths", []):
                            st.markdown(f'<span class="strength-tag">✓ {s}</span>', unsafe_allow_html=True)
                        st.markdown("")
                        st.markdown("**🔴 Gaps**")
                        for g in r.get("gaps", []):
                            st.markdown(f'<span class="gap-tag">✗ {g}</span>', unsafe_allow_html=True)
                    with d_col2:
                        st.markdown("**📁 Projects**")
                        for p in r.get("projects", []):
                            st.markdown(f"• {p}")
                    st.markdown("**📋 AI Summary**")
                    st.markdown(f'<div class="info-box">{r.get("summary", "")}</div>', unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

    with tab_all:
        render_candidates(results, tab_prefix="all")

    with tab_shortlisted:
        render_candidates([r for r in results if r.get("shortlisted")], tab_prefix="shortlisted")

    with tab_rejected:
        render_candidates([r for r in results if not r.get("shortlisted")], tab_prefix="rejected", show_form_gen=False)

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    df_data = []
    for r in results:
        df_data.append({
            "Name": r.get("candidate_name", ""),
            "Email": r.get("email", ""),
            "Score": r.get("match_score", 0),
            "Shortlisted": "Yes" if r.get("shortlisted") else "No",
            "Experience (yrs)": r.get("years_experience", 0),
            "Education": r.get("education", ""),
            "Skills": ", ".join(r.get("key_skills", [])),
            "Summary": r.get("summary", ""),
        })
    df = pd.DataFrame(df_data)
    st.download_button(
        "📥 Export Results as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="shortlisting_results.csv",
        mime="text/csv",
    )
