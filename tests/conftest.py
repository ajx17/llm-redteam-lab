import os

os.environ["LLM_PROVIDER"] = "mock"
os.environ["GUARDRAILS_ENABLED"] = "false"

import httpx  # noqa: E402  (env vars above must be set before the app's settings load)
import pytest  # noqa: E402

from app.config import settings  # noqa: E402
from app.guardrails import llama_guard  # noqa: E402


@pytest.fixture
def fake_guard(monkeypatch):
    """Turn both Llama Guard checks on and make it answer with whatever the test sets."""
    monkeypatch.setattr(settings, "guardrails_enabled", True)
    monkeypatch.setattr(settings, "input_guard_model", "llama-guard3:8b")
    monkeypatch.setattr(settings, "output_guard_model", "llama-guard3:8b")
    sent = {}

    def fake_post(url, json, timeout):
        sent["prompt"] = json["prompt"]
        request = httpx.Request("POST", url)
        return httpx.Response(200, json={"response": sent["answer"]}, request=request)

    monkeypatch.setattr(llama_guard.httpx, "post", fake_post)
    return sent
