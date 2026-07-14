"""
Simple JSON-based file storage for job criteria, candidates, and submissions.
For production, replace with a database (PostgreSQL, SQLite, etc.)
"""
import os
import json

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

CRITERIA_FILE = os.path.join(DATA_DIR, "job_criteria.json")
CANDIDATES_FILE = os.path.join(DATA_DIR, "candidates.json")
SUBMISSIONS_DIR = os.path.join(DATA_DIR, "submissions")
os.makedirs(SUBMISSIONS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Job Criteria
# ---------------------------------------------------------------------------

def save_job_criteria(criteria: dict):
    with open(CRITERIA_FILE, "w") as f:
        json.dump(criteria, f, indent=2)


def load_job_criteria() -> dict:
    if not os.path.exists(CRITERIA_FILE):
        return {}
    with open(CRITERIA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------------

def save_shortlisted_candidates(candidates: list):
    # Merge with existing to avoid overwrite on re-screen
    existing = {c.get("candidate_id"): c for c in load_shortlisted_candidates()}
    for c in candidates:
        cid = c.get("candidate_id", "")
        if cid:
            existing[cid] = c
    with open(CANDIDATES_FILE, "w") as f:
        json.dump(list(existing.values()), f, indent=2)


def load_shortlisted_candidates() -> list:
    if not os.path.exists(CANDIDATES_FILE):
        return []
    with open(CANDIDATES_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Submissions
# ---------------------------------------------------------------------------

def save_submission(submission: dict):
    cid = submission.get("candidate_id", "unknown")
    path = os.path.join(SUBMISSIONS_DIR, f"{cid}.json")
    with open(path, "w") as f:
        json.dump(submission, f, indent=2)


def load_all_submissions() -> list:
    submissions = []
    for fname in os.listdir(SUBMISSIONS_DIR):
        if fname.endswith(".json"):
            with open(os.path.join(SUBMISSIONS_DIR, fname)) as f:
                submissions.append(json.load(f))
    return submissions


def submission_exists(candidate_id: str) -> bool:
    path = os.path.join(SUBMISSIONS_DIR, f"{candidate_id}.json")
    return os.path.exists(path)
