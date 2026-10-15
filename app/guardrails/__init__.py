"""Guardrail pipeline. Every check is a no-op until we build it.

Planned checks (each one gets measured on its own):
- input:  Prompt Guard (injection/jailbreak classifier), Llama Guard (unsafe requests)
- output: canary-token leak check, Presidio PII redaction, Llama Guard (unsafe replies)
"""

from dataclasses import dataclass

from app.config import settings


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
    # TODO (step 1): import find_leaks at the top of this file.
    # TODO (step 2): run find_leaks on reply. If it found anything, return
    # Verdict(allowed=False, reason=...). The reason should say which kinds of
    # leak were found (like "output leak: canary") but never the leaked value.
    # Later: Presidio, Llama Guard
    return Verdict(allowed=True)
