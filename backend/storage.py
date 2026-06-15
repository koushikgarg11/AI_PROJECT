"""
File-based storage layer for candidates, responses, and uploaded files.
Uses JSON files for persistence and local directories for binary uploads.
"""

import json
import uuid
import shutil
from datetime import datetime
from pathlib import Path

# ── Directory Layout ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
RESUMES_DIR = UPLOADS_DIR / "resumes"
VIDEOS_DIR = UPLOADS_DIR / "videos"


def ensure_dirs():
    """Create all required directories if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


# ── API Key Persistence ───────────────────────────────────────────────────────

def save_api_key(api_key: str):
    """Save the Gemini API key locally so it survives app restarts."""
    ensure_dirs()
    config = _load_config()
    config["gemini_api_key"] = api_key
    _save_config(config)


def load_api_key() -> str:
    """Load the saved Gemini API key, or return empty string if not saved."""
    return _load_config().get("gemini_api_key", "")


def clear_api_key():
    """Remove the saved API key (e.g. if the user wants to reset it)."""
    config = _load_config()
    config.pop("gemini_api_key", None)
    _save_config(config)


def _load_config() -> dict:
    path = DATA_DIR / "config.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_config(config: dict):
    ensure_dirs()
    with open(DATA_DIR / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


# ── Criteria ──────────────────────────────────────────────────────────────────

def save_criteria(criteria: dict):
    ensure_dirs()
    with open(DATA_DIR / "criteria.json", "w", encoding="utf-8") as f:
        json.dump(criteria, f, indent=2)


def load_criteria() -> dict:
    path = DATA_DIR / "criteria.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ── Candidates ────────────────────────────────────────────────────────────────

def generate_candidate_id() -> str:
    """Generate a short unique 8-character uppercase ID."""
    return str(uuid.uuid4()).replace("-", "")[:8].upper()


def save_candidate(candidate_id: str, data: dict):
    """Upsert a candidate record into candidates.json."""
    ensure_dirs()
    candidates = load_all_candidates()
    candidates[candidate_id] = data
    with open(DATA_DIR / "candidates.json", "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2)


def load_all_candidates() -> dict:
    path = DATA_DIR / "candidates.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_candidate(candidate_id: str) -> dict:
    return load_all_candidates().get(candidate_id, {})


def delete_candidate(candidate_id: str):
    candidates = load_all_candidates()
    candidates.pop(candidate_id, None)
    with open(DATA_DIR / "candidates.json", "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2)


# ── Responses ─────────────────────────────────────────────────────────────────

def save_response(candidate_id: str, text_responses: dict, video_paths: dict):
    """
    Save a candidate's form submission.

    Args:
        candidate_id: Unique candidate ID
        text_responses: Dict mapping question_id -> answer text
        video_paths: Dict mapping question_id -> local file path string
    """
    ensure_dirs()
    all_responses = load_all_responses()
    all_responses[candidate_id] = {
        "submitted_at": datetime.now().isoformat(),
        "text_responses": text_responses,
        "video_paths": video_paths,
    }
    with open(DATA_DIR / "responses.json", "w", encoding="utf-8") as f:
        json.dump(all_responses, f, indent=2)


def load_all_responses() -> dict:
    path = DATA_DIR / "responses.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_response(candidate_id: str) -> dict:
    return load_all_responses().get(candidate_id, {})


# ── File Uploads ──────────────────────────────────────────────────────────────

def save_resume(candidate_id: str, file_bytes: bytes, filename: str) -> str:
    """Save a resume file and return its path string."""
    ensure_dirs()
    ext = Path(filename).suffix
    dest = RESUMES_DIR / f"{candidate_id}{ext}"
    dest.write_bytes(file_bytes)
    return str(dest)


def save_video(candidate_id: str, question_id: str, video_bytes: bytes, filename: str) -> str:
    """Save a video response and return its path string."""
    ensure_dirs()
    ext = Path(filename).suffix or ".mp4"
    dest = VIDEOS_DIR / f"{candidate_id}_{question_id}{ext}"
    dest.write_bytes(video_bytes)
    return str(dest)


def video_exists(path_str: str) -> bool:
    return path_str and Path(path_str).exists()


# ── Utilities ─────────────────────────────────────────────────────────────────

def clear_all_data():
    """Wipe all data and uploads. Use with caution."""
    for path in [DATA_DIR / "candidates.json", DATA_DIR / "responses.json"]:
        if path.exists():
            path.unlink()
    for folder in [RESUMES_DIR, VIDEOS_DIR]:
        if folder.exists():
            shutil.rmtree(folder)
    ensure_dirs()
