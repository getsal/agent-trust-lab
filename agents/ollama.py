"""Small Ollama HTTP client with raw-response and structured-output support."""
import json
from urllib.request import Request, urlopen


class OllamaError(RuntimeError):
    pass


def generate_raw(model: str, prompt: str, schema=None, base_url: str = "http://localhost:11434", timeout: int = 120) -> dict:
    body = {"model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0}}
    if schema is not None:
        body["format"] = schema
    payload = json.dumps(body).encode()
    request = Request(base_url.rstrip("/") + "/api/generate", data=payload,
                      headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read())
        if "response" not in data:
            raise OllamaError("Ollama response did not contain response")
        return data
    except Exception as exc:
        if isinstance(exc, OllamaError):
            raise
        raise OllamaError(f"Ollama unavailable: {exc}") from exc


def generate(model: str, prompt: str, base_url: str = "http://localhost:11434", timeout: int = 120) -> str:
    """Compatibility wrapper returning only the model's text response."""
    return str(generate_raw(model, prompt, base_url=base_url, timeout=timeout)["response"])
