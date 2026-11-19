import os

os.environ["LLM_PROVIDER"] = "mock"
os.environ["GUARDRAILS_ENABLED"] = "false"

import httpx  # noqa: E402  (env vars above must be set before the app's settings load)
import pytest  # noqa: E402

from app.config import settings  # noqa: E402
from app.guardrails import llama_guard, reply_judge  # noqa: E402


@pytest.fixture
def fake_guard(monkeypatch):
    """Turn the Llama Guard input check on and make it answer with whatever the test sets."""
    monkeypatch.setattr(settings, "guardrails_enabled", True)
    monkeypatch.setattr(settings, "input_guard_model", "llama-guard3:8b")
    sent = {}

    def fake_post(url, json, timeout):
        sent["prompt"] = json["prompt"]
        request = httpx.Request("POST", url)
        return httpx.Response(200, json={"response": sent["answer"]}, request=request)

    monkeypatch.setattr(llama_guard.httpx, "post", fake_post)
    return sent


@pytest.fixture
def fake_judge(monkeypatch):
    """Turn the reply judge on and make it answer with whatever the test sets."""
    monkeypatch.setattr(settings, "guardrails_enabled", True)
    monkeypatch.setattr(settings, "output_guard_model", "llama3.1:8b")
    sent = {}

    def fake_post(url, json, timeout):
        sent["review"] = json["messages"][1]["content"]
        request = httpx.Request("POST", url)
        body = {"message": {"content": sent["answer"]}}
        return httpx.Response(200, json=body, request=request)

    monkeypatch.setattr(reply_judge.httpx, "post", fake_post)
    return sent
