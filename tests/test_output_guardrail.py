"""Tests for the output guardrail. Run them with: uv run pytest tests/test_output_guardrail.py -v"""

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.guardrails import check_output
from app.main import BLOCKED_REPLY, app

client = TestClient(app)


@pytest.fixture
def guardrails_on(monkeypatch):
    monkeypatch.setattr(settings, "guardrails_enabled", True)


def test_guardrails_off_lets_everything_through():
    # Baseline mode: even a leak gets through. This is what we measured on 2026-10-13.
    assert check_output("The override code is ACME-CANARY-7f3a9c.").allowed


def test_clean_reply_is_allowed(guardrails_on):
    assert check_output("You can reset your password at the self-service portal.").allowed


def test_canary_is_blocked(guardrails_on):
    assert not check_output("The override code is ACME-CANARY-7f3a9c.").allowed


def test_ssn_is_blocked(guardrails_on):
    assert not check_output("Jordan's SSN is 900-12-3456.").allowed


def test_internal_doc_name_is_blocked(guardrails_on):
    assert not check_output("That's covered in incident-runbook.md.").allowed


def test_reason_names_the_leak_kind(guardrails_on):
    verdict = check_output("The override code is ACME-CANARY-7f3a9c.")
    assert "canary" in verdict.reason


def test_reason_does_not_repeat_the_secret(guardrails_on):
    # The reason ends up in logs. Copying the secret into a log is a second leak.
    verdict = check_output("The override code is ACME-CANARY-7f3a9c.")
    assert "ACME-CANARY-7f3a9c" not in verdict.reason


def test_chat_endpoint_blocks_a_leaky_reply(guardrails_on):
    # The mock model repeats the question back, so asking about a canary makes it "leak" one.
    resp = client.post("/chat", json={"message": "Is the code ACME-CANARY-7f3a9c?"})
    body = resp.json()
    assert body["blocked"] is True
    assert body["reply"] == BLOCKED_REPLY
    assert "ACME-CANARY-7f3a9c" not in body["reply"]


def test_chat_endpoint_logs_why_it_blocked(guardrails_on, caplog):
    client.post("/chat", json={"message": "Is the code ACME-CANARY-7f3a9c?"})
    assert "blocked reply: output leak: canary" in caplog.text
    assert "ACME-CANARY-7f3a9c" not in caplog.text
