"""
Resume shortlisting logic using Google Gemini.
Analyzes resume text against job criteria and returns a structured assessment.
"""

import json
import re
from backend.gemini_client import generate_content


def shortlist_resume(model, resume_text: str, criteria: dict, preferred_model: str = "gemini-1.5-flash") -> dict:
    """
    Use Gemini to analyze a single resume against job criteria.

    Args:
        model: Initialized Gemini model instance
        resume_text: Plain text extracted from the resume
        criteria: Dict with keys: job_title, skills, min_experience, education, additional

    Returns:
        Dict with candidate assessment including match_score and shortlisted flag
    """
    skills_str = ", ".join(criteria.get("skills", [])) if criteria.get("skills") else "Not specified"
    prompt = f"""
You are a senior HR recruiter with 15+ years of experience. Analyze this resume against the job criteria below.

JOB CRITERIA:
- Job Title: {criteria.get("job_title", "Not specified")}
- Required Skills: {skills_str}
- Minimum Experience: {criteria.get("min_experience", 0)} years
- Education Required: {criteria.get("education", "Any")}
- Additional Requirements: {criteria.get("additional", "None")}

RESUME TEXT:
{resume_text[:5000]}

Analyze carefully and respond ONLY with a single valid JSON object. No markdown, no code blocks, no explanation.

{{
    "candidate_name": "Full name extracted from resume",
    "email": "Email address or empty string",
    "phone": "Phone number or empty string",
    "match_score": <integer 0-100>,
    "shortlisted": <true if score >= 60, else false>,
    "years_experience": <estimated years as number>,
    "education": "Highest education qualification",
    "key_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
    "projects": ["Brief project 1 description", "Brief project 2 description"],
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "gaps": ["Gap 1 if any", "Gap 2 if any"],
    "summary": "2-3 sentence honest recruiter assessment of this candidate"
}}
"""
    raw = generate_content(model, prompt, preferred_model=preferred_model).strip()

    # Strip markdown code fences if Gemini wrapped the response
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON from within the text
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise ValueError(f"Gemini returned unparseable response: {raw[:200]}")

    # Ensure required fields exist
    result.setdefault("candidate_name", "Unknown Candidate")
    result.setdefault("email", "")
    result.setdefault("phone", "")
    result.setdefault("match_score", 0)
    result.setdefault("shortlisted", False)
    result.setdefault("years_experience", 0)
    result.setdefault("education", "Not specified")
    result.setdefault("key_skills", [])
    result.setdefault("projects", [])
    result.setdefault("strengths", [])
    result.setdefault("gaps", [])
    result.setdefault("summary", "No summary available.")

    return result
