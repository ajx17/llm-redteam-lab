"""Guardrail pipeline. Checks run only when GUARDRAILS_ENABLED=true.

Built so far:
- output: leak check (canary tokens, SSNs, internal doc names, internal values)
- input:  Llama Guard 3 with our own categories (only when INPUT_GUARD_MODEL is set)
- output: Llama Guard 3 on the reply, for made-up records and claimed actions
          (only when OUTPUT_GUARD_MODEL is set)

Planned (each one gets measured on its own):
- input:  Prompt Guard (injection/jailbreak classifier)
- output: Presidio PII redaction
"""

from dataclasses import dataclass

from app.config import settings
from app.guardrails import llama_guard
from app.guardrails.leaks import find_leaks


@dataclass
class Verdict:
    allowed: bool
    reason: str = ""


def check_input(message: str) -> Verdict:
    if not settings.guardrails_enabled or not settings.input_guard_model:
        return Verdict(allowed=True)

    safe, categories = llama_guard.classify(message)
    if not safe:
        return Verdict(allowed=False, reason="input unsafe: " + categories)

    # TODO: Prompt Guard
    return Verdict(allowed=True)


def check_output(reply: str, message: str = "") -> Verdict:
    if not settings.guardrails_enabled:
        return Verdict(allowed=True)

    leaks = find_leaks(reply)
    if leaks:
        # Only name the kinds. The reason can end up in logs, so the secret stays out of it.
        kinds = sorted({leak.kind for leak in leaks})
        return Verdict(allowed=False, reason="output leak: " + ", ".join(kinds))

    if settings.output_guard_model:
        safe, categories = llama_guard.classify(message, reply=reply)
        if not safe:
            return Verdict(allowed=False, reason="reply unsafe: " + categories)

    # TODO: Presidio
    return Verdict(allowed=True)
