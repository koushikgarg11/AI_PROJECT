"""
Backend AI logic: resume screening + question generation using Gemini API.

The Gemini API key is no longer read from an environment variable / Streamlit
secret. Every function here that needs to call Gemini takes an `api_key`
argument instead, so each visitor's own key (held in st.session_state on the
frontend) is used for their own requests.
"""

import os
import json
import re
import uuid
from google import genai

GEMINI_MODEL = "gemini-2.0-flash"


# ---------------------------------------------------------------------------
# Text extraction helpers (no API key needed)
# ---------------------------------------------------------------------------

def extract_text_from_file(filepath: str) -> str:
    """Extract raw text from a PDF or DOCX file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return _extract_pdf(filepath)
    elif ext == ".docx":
        return _extract_docx(filepath)
    return ""


def _extract_pdf(filepath: str) -> str:
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
        return "\n".join(parts)
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def _extract_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        return f"[DOCX extraction error: {e}]"


# ---------------------------------------------------------------------------
# Gemini call helpers
# ---------------------------------------------------------------------------

def _get_client(api_key: str) -> genai.Client:
    if not api_key:
        raise ValueError("No Gemini API key provided. Each user must supply their own key.")
    return genai.Client(api_key=api_key)


def _call_gemini(prompt: str, api_key: str, max_tokens: int = 1500) -> str:
    """Call Gemini with the given user's API key and return the text response."""
    client = _get_client(api_key)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text.strip()


def _parse_json(raw: str):
    """Strip markdown fences and parse JSON."""
    raw = re.sub(r"^```[a-z]*\n?", "", raw.strip())
    raw = re.sub(r"\n?```$", "", raw).strip()
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Resume screening
# ---------------------------------------------------------------------------

def screen_resumes(file_paths: list, criteria: dict, api_key: str) -> list:
    """
    Screen a list of resume files against job criteria using the caller's
    own Gemini API key.
    Returns a list of candidate dicts with scores and shortlist decisions.
    """
    results = []
    for path in file_paths:
        resume_text = extract_text_from_file(path)
        result = _evaluate_single_resume(resume_text, os.path.basename(path), criteria, api_key)
        result["filename"] = os.path.basename(path)
        result["candidate_id"] = str(uuid.uuid4())[:8]
        result["job_title"] = criteria.get("job_title", "")
        result["company"] = criteria.get("company", "")
        # Store full resume text for personalized question generation
        result["_resume_text"] = resume_text
        results.append(result)
    return results


def _evaluate_single_resume(resume_text: str, filename: str, criteria: dict, api_key: str) -> dict:
    """Use Gemini to evaluate one resume and return structured data."""

    threshold = criteria.get("shortlist_threshold", 65)
    must_have = ", ".join(criteria.get("must_have_skills", []))
    nice_to_have = ", ".join(criteria.get("nice_to_have_skills", []))

    prompt = f"""You are an expert HR recruiter. Evaluate this resume against the job criteria.

## Job Criteria
- Role: {criteria.get("job_title", "N/A")}
- Company: {criteria.get("company", "N/A")}
- Experience Required: {criteria.get("experience_min", 0)}–{criteria.get("experience_max", 10)} years
- Must-Have Skills: {must_have}
- Nice-to-Have Skills: {nice_to_have}
- Minimum Education: {criteria.get("education", "Any")}
- Additional Notes: {criteria.get("additional_criteria", "None")}

## Resume
{resume_text[:6000]}

## Instructions
Score the candidate 0–100 based on fit. Shortlist if score >= {threshold}.

For "projects", extract DETAILED descriptions (2–3 sentences each) that include:
- The project name or domain
- Technologies/tools used
- What problem it solved or what the candidate built

Return ONLY valid JSON with these exact keys:
{{
  "name": "Full name or 'Unknown'",
  "email": "Email or 'N/A'",
  "phone": "Phone or 'N/A'",
  "score": <integer 0-100>,
  "shortlisted": <true or false>,
  "summary": "2-sentence candidate summary",
  "reasoning": "3-4 sentences explaining score and shortlist decision",
  "skills_found": ["specific skill 1", "specific skill 2", ...],
  "projects": [
    "Project Name / Domain: Built X using Y and Z to solve W. Achieved/resulted in Q.",
    "Project Name / Domain: ..."
  ],
  "experience_years": <number>
}}

Return only the JSON, no other text."""

    try:
        raw = _call_gemini(prompt, api_key)
        return _parse_json(raw)
    except Exception as e:
        return {
            "name": "Unknown", "email": "N/A", "phone": "N/A",
            "score": 0, "shortlisted": False,
            "summary": "Could not parse resume.",
            "reasoning": f"Error: {e}",
            "skills_found": [], "projects": [], "experience_years": 0,
        }


# ---------------------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------------------

def generate_candidate_questions(candidate: dict, api_key: str) -> list:
    """
    Generate assessment questions for a shortlisted candidate.
    - First 3: Fixed ACC company-fit questions (vision, mission, startup culture)
    - Next 5: Personalized to the candidate's resume (skills + projects), kept concise
    Returns a list of question dicts with type: 'company', 'skill', 'project', or 'video'.
    """

    # ── Fixed ACC company-fit questions (always first, never change) ──────────
    company_questions = [
        {
            "type": "company",
            "question": "Analytics Career Connect is on a mission to bridge India's skill-to-job gap for students from Tier 2, 3, and 4 cities. How does this mission resonate with you personally, and why do you want to be part of it?"
        },
        {
            "type": "company",
            "question": "ACC operates with a 'learning by doing' philosophy — real projects, deadlines, and a startup pace. Give a specific example from your past where you thrived (or struggled) in a similar fast-paced, hands-on environment."
        },
        {
            "type": "company",
            "question": "In a startup like ACC, roles are fluid and ownership matters. What's one initiative you'd take in the first 30 days to add value — and why that specifically?"
        },
    ]

    # ── Personalized resume-based questions (generated by Gemini) ────────────
    skills = candidate.get("skills_found", [])
    projects = candidate.get("projects", [])
    job_title = candidate.get("job_title", "the role")
    name = candidate.get("name", "the candidate")
    experience = candidate.get("experience_years", 0)
    resume_text = candidate.get("_resume_text", "")

    skills_str = "\n".join(f"  - {s}" for s in skills) if skills else "  - Not specified"
    projects_str = "\n".join(f"  - {p}" for p in projects) if projects else "  - None listed"

    prompt = f"""You are a senior technical interviewer. Generate 5 SHORT, SHARP, PERSONALIZED interview questions for this candidate.

STRICT RULES:
1. Each question must be ONE sentence only — no multi-part questions, no explanations.
2. Skill questions MUST name a specific tool/technology from their skills list.
3. Project questions MUST name or clearly reference a specific project from their profile.
4. NO generic questions (e.g. "Tell me about a project" is banned).
5. Video questions must be under 20 words and reference their role or background.

GOOD example: "In your fraud detection project, how did you handle class imbalance with XGBoost?"
BAD example: "Can you describe a challenging project you worked on and how you overcame obstacles in it?"

## Candidate
- Name: {name}
- Role: {job_title}
- Experience: {experience} years
- Skills: {skills_str}
- Projects: {projects_str}

## Resume (for deeper context)
{resume_text[:4000]}

Generate exactly 5 questions:
- 2 skill questions (type: "skill")
- 2 project questions (type: "project")
- 1 video question (type: "video", max 20 words)

Return ONLY a valid JSON array, no markdown, no preamble:
[
  {{"type": "skill", "question": "...one sentence..."}},
  {{"type": "skill", "question": "...one sentence..."}},
  {{"type": "project", "question": "...one sentence..."}},
  {{"type": "project", "question": "...one sentence..."}},
  {{"type": "video", "question": "...max 20 words..."}}
]"""

    try:
        raw = _call_gemini(prompt, api_key, max_tokens=800)
        personalized = _parse_json(raw)
        if not isinstance(personalized, list):
            raise ValueError("Response is not a list")
    except Exception as e:
        top_skill = skills[0] if skills else "your primary skill"
        top_project = projects[0][:60] if projects else "your most significant project"
        personalized = [
            {"type": "skill", "question": f"What's the hardest bug you've debugged while working with {top_skill}?"},
            {"type": "skill", "question": f"When would you NOT use {top_skill} — and what would you pick instead?"},
            {"type": "project", "question": f"What was the single biggest technical risk in {top_project} and how did you mitigate it?"},
            {"type": "project", "question": f"If you rebuilt {top_project} today, what one decision would you change?"},
            {"type": "video", "question": f"In 90 seconds, tell us why you're the right {job_title} for ACC."},
        ]

    return company_questions + personalized
