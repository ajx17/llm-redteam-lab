"""Guardrail pipeline. Checks run only when GUARDRAILS_ENABLED=true.

Built so far:
- output: leak check (canary tokens, SSNs, internal doc names)

Planned (each one gets measured on its own):
- input:  Prompt Guard (injection/jailbreak classifier), Llama Guard (unsafe requests)
- output: Presidio PII redaction, Llama Guard (unsafe replies)
"""

from dataclasses import dataclass

from app.config import settings
from app.guardrails.leaks import find_leaks


@dataclass
class Verdict:
    allowed: bool
    reason: str = ""


def check_input(message: str) -> Verdict:
    if not settings.guardrails_enabled:
        return Verdict(allowed=True)
    # TODO: Prompt Guard + Llama Guard
    return Verdict(allowed=True)


def check_output(reply: str) -> Verdict:
    if not settings.guardrails_enabled:
        return Verdict(allowed=True)

    leaks = find_leaks(reply)
    if leaks:
        # Only name the kinds. The reason can end up in logs, so the secret stays out of it.
        kinds = sorted({leak.kind for leak in leaks})
        return Verdict(allowed=False, reason="output leak: " + ", ".join(kinds))

    # TODO: Presidio, Llama Guard
    return Verdict(allowed=True)
