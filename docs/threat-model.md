# Threat Model: AcmeBot

Status: draft. Fill in as attacks and defenses are built.

## System

AcmeBot is an internal IT helpdesk chatbot. An employee sends a question, the app
retrieves matching paragraphs from company documents, and a language model answers
using that context.

## Assets worth protecting

| Asset | Where it lives | Canary |
|---|---|---|
| System prompt and admin override code | `app/main.py` | ACME-CANARY-7f3a9c |
| Internal incident runbook | `data/docs/internal/` | ACME-CANARY-91d2e4 |
| Employee personal data (fake) | `data/docs/internal/` | ACME-CANARY-c48b02 |

## Trust boundaries

1. Employee input enters the app (untrusted).
2. Retrieved documents enter the prompt (partly trusted: a poisoned doc is an attack path).
3. Model output returns to the employee (must be checked before it leaves).

## Threats mapped to OWASP Top 10 for LLM Applications (2025) and MITRE ATLAS

| OWASP LLM | Threat in AcmeBot | MITRE ATLAS | Test source | Defense (planned) | Baseline result | Defended result |
|---|---|---|---|---|---|---|
| LLM01 Prompt Injection | User tells the bot to ignore its rules | AML.T0051 LLM Prompt Injection | promptfoo, garak | Prompt Guard | TBD | TBD |
| LLM01 Indirect injection | Instructions hidden inside a retrieved doc | AML.T0051.001 Indirect | custom | Prompt Guard on context | TBD | TBD |
| LLM02 Sensitive Info Disclosure | Bot reveals HR data or runbook | AML.T0057 LLM Data Leakage | promptfoo `pii` | Doc access control, Presidio, canary check | TBD | TBD |
| LLM07 System Prompt Leakage | Bot reveals its instructions and override code | AML.T0056 Meta Prompt Extraction | promptfoo `prompt-extraction` | Canary check, no secrets in prompt | TBD | TBD |
| LLM06 Excessive Agency | Bot claims or performs admin actions | AML.T0053 LLM Plugin Compromise | promptfoo `excessive-agency` | Least-privilege tools | TBD | TBD |
| LLM05 Improper Output Handling | Reply contains unsafe content or markup | | Llama Guard | Llama Guard on output | TBD | TBD |

Verify ATLAS technique IDs against https://atlas.mitre.org before publishing.

## Out of scope (for now)

Model supply chain (LLM03), training data poisoning (LLM04), denial of service (LLM10).
