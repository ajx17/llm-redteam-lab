"""Model providers. Ollama runs a free local model; mock returns canned text for CI."""

import httpx

from app.config import settings


def generate(system_prompt: str, user_message: str) -> str:
    if settings.llm_provider == "mock":
        return _mock(system_prompt, user_message)
    if settings.llm_provider == "ollama":
        return _ollama(system_prompt, user_message)
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")


def _ollama(system_prompt: str, user_message: str) -> str:
    resp = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        json={
            "model": settings.ollama_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _mock(system_prompt: str, user_message: str) -> str:
    return f"[mock] You asked: {user_message}"
