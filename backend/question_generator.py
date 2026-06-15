"""
Interview question generation using Google Gemini.
Generates personalized skill, project, and communication questions
for each shortlisted candidate based on their resume.
"""

import json
import re
from backend.gemini_client import generate_content


def generate_interview_questions(model, resume_data: dict, resume_text: str, preferred_model: str = "gemini-2.5-flash") -> dict:
    """
    Generate a personalized set of interview questions for a candidate.

    Args:
        model: Initialized Gemini model instance
        resume_data: Structured assessment from shortlister (has key_skills, projects, etc.)
        resume_text: Original resume text for deeper context

    Returns:
        Dict with skill_questions, project_questions, and communication_questions
    """
    skills_str = ", ".join(resume_data.get("key_skills", [])) or "General skills"
    projects_str = "; ".join(resume_data.get("projects", [])) or "No specific projects"
    experience = resume_data.get("years_experience", 0)
    name = resume_data.get("candidate_name", "the candidate")

    prompt = f"""
You are a technical interview expert. Generate highly specific, personalized interview questions for this candidate.

CANDIDATE PROFILE:
- Name: {name}
- Key Skills: {skills_str}
- Projects: {projects_str}
- Years of Experience: {experience}

RESUME EXCERPT (for context):
{resume_text[:3500]}

Generate exactly the following structure. Make every question SPECIFIC to this candidate's actual skills and projects — not generic.
Respond ONLY with valid JSON. No markdown, no code blocks.

{{
    "skill_questions": [
        {{"id": "sq1", "question": "Specific technical question about their primary skill", "placeholder": "Describe your approach..."}},
        {{"id": "sq2", "question": "Specific question about their secondary skill or tool", "placeholder": "Explain how you..."}},
        {{"id": "sq3", "question": "Scenario or problem-solving question relevant to their tech stack", "placeholder": "Walk me through..."}}
    ],
    "project_questions": [
        {{"id": "pq1", "question": "Deep-dive question about their most significant project", "placeholder": "Tell me about the architecture..."}},
        {{"id": "pq2", "question": "Question about challenges or technical decisions in a specific project", "placeholder": "What was the toughest part..."}}
    ],
    "communication_questions": [
        {{"id": "cq1", "question": "Please record a 1–2 minute video introducing yourself, your professional background, and what excites you about this opportunity.", "type": "video", "max_size_mb": 100}},
        {{"id": "cq2", "question": "Please record a 1–2 minute video describing the most challenging technical problem you've faced in your career and how you resolved it.", "type": "video", "max_size_mb": 100}}
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
        {"id": "cq1", "question": "Please record a 1–2 minute video introducing yourself.", "type": "video", "max_size_mb": 100},
        {"id": "cq2", "question": "Please record a 1–2 minute video describing a challenge you overcame.", "type": "video", "max_size_mb": 100}
    ])

    return result
