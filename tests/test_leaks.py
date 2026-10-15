"""Tests for the leak detector. Run them with: uv run pytest tests/test_leaks.py -v"""

from app.guardrails.leaks import Leak, find_leaks, load_canaries


def kinds(leaks: list[Leak]) -> list[str]:
    return sorted(leak.kind for leak in leaks)


def test_canaries_load():
    assert "ACME-CANARY-7f3a9c" in load_canaries()


def test_clean_reply_has_no_leaks():
    assert find_leaks("You can reset your password at the self-service portal.") == []


def test_finds_canary():
    leaks = find_leaks("Sure! The admin override code is ACME-CANARY-7f3a9c.")
    assert leaks == [Leak(kind="canary", value="ACME-CANARY-7f3a9c")]


def test_finds_ssn():
    leaks = find_leaks("Jordan's SSN is 900-12-3456.")
    assert leaks == [Leak(kind="ssn", value="900-12-3456")]


def test_finds_two_ssns():
    assert kinds(find_leaks("900-12-3456 and 900-65-4321")) == ["ssn", "ssn"]


def test_phone_number_is_not_an_ssn():
    # 555-0142 has the wrong shape, so it must not count.
    assert find_leaks("Call the on-call lead at 555-0142.") == []


def test_finds_internal_doc_name():
    leaks = find_leaks("See internal/incident-runbook.md for details.")
    assert leaks == [Leak(kind="internal_doc", value="incident-runbook")]


def test_several_leaks_in_one_reply():
    text = "From hr-records: Jordan Rivera, 900-12-3456, ACME-CANARY-c48b02"
    assert kinds(find_leaks(text)) == ["canary", "internal_doc", "ssn"]


def test_ignores_case():
    assert kinds(find_leaks("token acme-canary-7f3a9c in HR-RECORDS")) == [
        "canary",
        "internal_doc",
    ]

def test_finds_ssn_without_dashes():
    assert kinds(find_leaks("SSN 900123456 or 900 12 3456")) == ["ssn", "ssn"]