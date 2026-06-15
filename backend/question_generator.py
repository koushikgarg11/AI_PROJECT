"""
Interview question generation using Google Gemini.
Generates personalized skill, project, and communication questions
for each shortlisted candidate based on their resume.
"""

import json
import re
from backend.gemini_client import generate_content


def generate_interview_questions(
    model,
    resume_data: dict,
    resume_text: str,
    preferred_model: str = "gemini-2.5-flash",
    criteria: dict = None,
) -> dict:
    """
    Generate a personalized set of interview questions for a candidate.

    Args:
        model: Initialized Gemini model instance
        resume_data: Structured assessment from shortlister
        resume_text: Original resume text for deeper context
        preferred_model: Gemini model string
        criteria: Job criteria dict (job_title, skills, etc.) for role-targeted questions

    Returns:
        Dict with skill_questions, project_questions, and communication_questions
    """
    skills = resume_data.get("key_skills", [])
    projects = resume_data.get("projects", [])
    experience = resume_data.get("years_experience", 0)
    name = resume_data.get("candidate_name", "the candidate")
    strengths = resume_data.get("strengths", [])
    gaps = resume_data.get("gaps", [])

    # Format lists for the prompt
    skills_str = "\n".join(f"  - {s}" for s in skills) if skills else "  - Not specified"
    projects_str = "\n".join(f"  - {p}" for p in projects) if projects else "  - No specific projects listed"
    strengths_str = ", ".join(strengths) if strengths else "N/A"
    gaps_str = ", ".join(gaps) if gaps else "None"

    # Job context (if available)
    job_title = criteria.get("job_title", "the role") if criteria else "the role"
    job_skills = ", ".join(criteria.get("skills", [])) if criteria else ""
    job_context = f"""
TARGET JOB:
- Role: {job_title}
- Required Skills: {job_skills or 'Not specified'}
- Additional Requirements: {criteria.get('additional', 'None') if criteria else 'N/A'}
""" if criteria else ""

    # Use more of the resume for context (up to 6000 chars)
    resume_excerpt = resume_text[:6000].strip()

    prompt = f"""You are a senior technical interviewer. Your task is to generate HIGHLY SPECIFIC, NON-GENERIC interview questions tailored ONLY to this individual candidate. Every question must reference something concrete from their resume — a specific technology they used, a specific project they built, a specific decision they made.

CANDIDATE: {name}
EXPERIENCE: {experience} years
{job_context}
SKILLS EXTRACTED FROM RESUME:
{skills_str}

PROJECTS EXTRACTED FROM RESUME:
{projects_str}

CANDIDATE STRENGTHS: {strengths_str}
IDENTIFIED GAPS: {gaps_str}

FULL RESUME TEXT (use this for deeper context):
{resume_excerpt}

INSTRUCTIONS:
- Read the full resume carefully before writing any question.
- Each skill question must name a specific technology/tool/concept from THEIR resume (not a generic one).
- Each project question must name or clearly reference a SPECIFIC project from their resume, ask about a concrete technical decision, architecture choice, or problem they solved.
- Do NOT write questions that could apply to any candidate (e.g. "Tell me about a project you worked on" is BAD).
- Good example: "In your {projects[0] if projects else 'ML project'}, how did you handle model drift in production?" 
- If they have a gap (e.g. missing skill), write one question probing how they would approach it.
- Keep questions concise and direct — no fluff.

Respond ONLY with valid JSON. No markdown, no code blocks, no preamble.

{{
    "skill_questions": [
        {{"id": "sq1", "question": "<specific technical question about their PRIMARY skill with concrete scenario>", "placeholder": "<relevant hint referencing their specific background>"}},
        {{"id": "sq2", "question": "<specific question about a SECONDARY skill or tool they used, naming it explicitly>", "placeholder": "<relevant hint>"}},
        {{"id": "sq3", "question": "<a scenario or debugging question grounded in their actual tech stack and experience level>", "placeholder": "<relevant hint>"}}
    ],
    "project_questions": [
        {{"id": "pq1", "question": "<deep-dive into their most significant project — name it explicitly and ask about a specific technical choice>", "placeholder": "<relevant hint>"}},
        {{"id": "pq2", "question": "<question about a challenge, tradeoff, or failure in a specific project — name the project>", "placeholder": "<relevant hint>"}}
    ],
    "communication_questions": [
        {{"id": "cq1", "question": "Please record a 1–2 minute video introducing yourself, your background as a {job_title}, and why this opportunity excites you.", "type": "video", "max_size_mb": 100}},
        {{"id": "cq2", "question": "Please record a 1–2 minute video walking us through the most technically complex problem you solved{' in your ' + projects[0] if projects else ''} or in your career, and how you resolved it.", "type": "video", "max_size_mb": 100}}
    ]
}}
"""

    raw = generate_content(model, prompt, preferred_model=preferred_model).strip()

    # Strip markdown code fences
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise ValueError(f"Gemini returned unparseable questions: {raw[:200]}")

    # Validate structure
    result.setdefault("skill_questions", [])
    result.setdefault("project_questions", [])
    result.setdefault("communication_questions", [
        {"id": "cq1", "question": f"Please record a 1–2 minute video introducing yourself and your interest in the {job_title} role.", "type": "video", "max_size_mb": 100},
        {"id": "cq2", "question": "Please record a 1–2 minute video describing the most challenging technical problem you've solved and how you resolved it.", "type": "video", "max_size_mb": 100},
    ])

    return result
