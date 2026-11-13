"""Provider discovery metadata for the localhost UI.

Cloud providers are intentionally discovery-only in this pass; no billable
request is made merely to populate the selectors.
"""
import json
import os
from urllib.request import urlopen


def ollama_models(base_url="http://localhost:11434", timeout=2):
    try:
        with urlopen(base_url.rstrip("/") + "/api/tags", timeout=timeout) as response:
            data = json.loads(response.read())
        return {"available": True, "models": [m.get("name") for m in data.get("models", []) if m.get("name")], "message": "Ollama is reachable"}
    except Exception as exc:
        return {"available": False, "models": [], "message": f"Ollama unavailable: {exc}"}


def provider_catalog():
    catalog = {"ollama": {"label": "Ollama · local", **ollama_models()},
               "offline": {"label": "Offline replay · simulated", "available": True, "models": ["offline-a", "offline-b"], "message": "No model call; deterministic replay"}}
    for key, env_name, label in (("openai", "OPENAI_API_KEY", "OpenAI · cloud"), ("anthropic", "ANTHROPIC_API_KEY", "Anthropic · cloud"), ("gemini", "GEMINI_API_KEY", "Google Gemini · cloud")):
        configured = bool(os.environ.get(env_name))
        catalog[key] = {"label": label, "available": False, "configured": configured, "models": [], "message": "Configured but cloud execution is experimental and disabled in this pass" if configured else f"Missing {env_name}"}
    return catalog
