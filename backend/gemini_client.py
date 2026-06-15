"""
Gemini API client wrapper.
Uses the current google-genai SDK (v1 API) with automatic model fallback.

Validation strategy:
- Uses models.list() to verify the key (ZERO quota consumed)
- Only tries generate_content to find an available model after key is confirmed valid
"""

from google import genai

# Models tried in order when a quota error is hit.
# Each has its own independent free-tier quota.
FALLBACK_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
]


def initialize_gemini(api_key: str) -> genai.Client:
    """
    Create a Gemini client.  Forces api_version='v1' so that stable
    models (gemini-1.5-flash, etc.) are available alongside v2 models.
    """
    return genai.Client(
        api_key=api_key,
        http_options={"api_version": "v1"},
    )


def generate_content(client: genai.Client, prompt: str, preferred_model: str = "gemini-1.5-flash") -> str:
    """
    Send a prompt and return the text response.
    Auto-falls back through FALLBACK_MODELS if quota is exhausted.
    """
    order = [preferred_model] + [m for m in FALLBACK_MODELS if m != preferred_model]
    last_error = None

    for model in order:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            err_str = str(e)
            if any(kw in err_str for kw in ["429", "RESOURCE_EXHAUSTED", "quota", "NOT_FOUND", "404"]):
                last_error = f"{model}: {'quota exceeded' if '429' in err_str else 'not available'}"
                continue
            raise  # Hard error — bad key, network, etc.

    raise RuntimeError(
        f"All models are quota-limited right now ({last_error}). "
        "Please wait a few minutes and try again."
    )


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """
    Validate API key WITHOUT consuming any generation quota.
    Uses models.list() to verify the key, then optionally probes for a working model.

    Returns:
        (True,  model_name)       — key is valid AND a model has quota
        (True,  "quota_exhausted")— key is valid BUT all models are at their limit
        (False, error_message)    — key is invalid or unreachable
    """
    # ── Step 1: Verify the key is real (no generation quota used) ────────────
    try:
        client = initialize_gemini(api_key)
        _ = list(client.models.list())   # lightweight auth check
    except Exception as e:
        err = str(e)
        if "API_KEY_INVALID" in err or "401" in err or "403" in err or "invalid" in err.lower():
            return False, "Invalid API key — please double-check and try again."
        return False, f"Could not reach Gemini API: {err[:200]}"

    # ── Step 2: Find the first model with available quota ────────────────────
    for model in FALLBACK_MODELS:
        try:
            client.models.generate_content(model=model, contents="Say OK")
            return True, model
        except Exception as e:
            err_str = str(e)
            if any(kw in err_str for kw in ["429", "RESOURCE_EXHAUSTED", "quota", "NOT_FOUND", "404"]):
                continue          # try next model
            return False, f"Unexpected error on {model}: {err_str[:150]}"

    # Key is valid but every model is currently rate-limited
    return True, "quota_exhausted"
