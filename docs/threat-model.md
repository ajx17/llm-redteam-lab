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

## Threats mapped to OWASP Top 10 for LLM Applications (2026) and MITRE ATLAS

OWASP IDs follow the [2026 edition](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)
(published August 2026). ATLAS IDs were checked against ATLAS data release 2026.09
([atlas-data](https://github.com/mitre-atlas/atlas-data), `dist/v6/ATLAS-2026.09.yaml`).

| OWASP LLM (2026) | Threat in AcmeBot | MITRE ATLAS | Test source | Defense (planned) | Baseline result | Defended result |
|---|---|---|---|---|---|---|
| LLM01 Prompt Injection | User tells the bot to ignore its rules | AML.T0051.000 LLM Prompt Injection: Direct; AML.T0054 LLM Jailbreak | promptfoo `hijacking`, jailbreak strategies; garak | Prompt Guard | TBD | TBD |
| LLM01 Prompt Injection (indirect) | Instructions hidden inside a retrieved doc | AML.T0051.001 LLM Prompt Injection: Indirect; AML.T0070 RAG Poisoning | custom | Prompt Guard on retrieved context | TBD | TBD |
| LLM02 Sensitive Information Disclosure | Bot reveals HR data or the incident runbook | AML.T0057 LLM Data Leakage; AML.T0085.000 Data from AI Services: RAG Databases | promptfoo `pii` | Doc access control, Presidio, canary check | TBD | TBD |
| LLM03 Excessive Agency | Bot claims to perform admin actions (resets, unlocks) it has no authority for | AML.T0053 AI Agent Tool Invocation | promptfoo `excessive-agency` | Least-privilege tools, human approval | TBD | TBD |
| LLM07 Misinformation | Bot invents links, policies or document sections and states them as fact | AML.T0062 Discover LLM Hallucinations | promptfoo `hallucination` (planned) | Answer only from retrieved sources, cite them | TBD | TBD |
| LLM08 Hidden Context Exposure | Bot reveals its system prompt, override code, or hidden retrieved context | AML.T0056 Extract LLM System Prompt; AML.T0069.002 Discover LLM System Information: System Prompt | promptfoo `prompt-extraction` | Canary check, no secrets in the prompt | TBD | TBD |
| LLM10 Improper Output Handling | Reply contains markup or links a client would render or fetch | AML.T0077 LLM Response Rendering | Llama Guard, custom | Output encoding, Llama Guard on output | TBD | TBD |

AcmeBot has no real tools yet, so LLM03 findings are the bot *claiming* actions it
cannot take. They become true tool-invocation tests once a tool is added.

### What changed from the 2025 list

| 2025 | 2026 |
|---|---|
| LLM06 Excessive Agency | LLM03 Excessive Agency |
| LLM07 System Prompt Leakage | LLM08 Hidden Context Exposure (wider: any hidden context, including retrieved docs) |
| LLM05 Improper Output Handling | LLM10 Improper Output Handling |
| LLM09 Misinformation | LLM07 Misinformation |
| ATLAS AML.T0053 "LLM Plugin Compromise" | AML.T0053 "AI Agent Tool Invocation" (renamed) |
| ATLAS AML.T0056 "LLM Meta Prompt Extraction" | AML.T0056 "Extract LLM System Prompt" (renamed) |

## Leak detector: SSN detection decisions

The leak detector (`app/guardrails/leaks.py`) flags SSNs with a regular expression.
These are the choices behind it and the gaps we know about.

| Question | Decision | Why |
|---|---|---|
| Dashed format (`900-12-3456`)? | Detected | The standard written form, and the form our test data uses. |
| No separators (`900123456`) or spaces (`900 12 3456`)? | Detect with optional separators: `\b\d{3}[- ]?\d{2}[- ]?\d{4}\b` | A bot asked to "reformat" data can drop the dashes. Bare 9-digit numbers (order or ticket IDs) will also match. For a leak detector, a false alarm costs less than a missed SSN. |
| Invalid prefixes (`000`, `666`, `9xx`)? | Not rejected | Real SSNs never start with these, so production detectors filter them to cut false positives. Our fake SSNs use `900-` on purpose so they can never belong to a real person, and filtering would hide them. |
| Phone numbers? | Not matched | US numbers are 10 digits (`508-555-0142`) or 7 (`555-0142`), never 3-2-4. A unit test checks this. |
| Other countries' IDs (UK National Insurance `AB123456C`, Canada SIN, and so on)? | Out of scope | AcmeBot's data is US-only. Microsoft Presidio, planned for the output guardrail, has recognizers for many countries. |

### What regex cannot catch

A pattern only finds text in the shape it expects. An attacker can ask the bot to:

- spell the number out ("nine zero zero, one two...")
- encode it (base64, hex, reversed digits)
- split it across sentences or turns
- insert other characters (`9.0.0-1.2-3.4.5.6`)

None of these will match. The detector is a last line of defense on the output, not
the main control. The real fix is upstream: AcmeBot should never be able to retrieve
HR records for a user who isn't allowed to see them (document access control,
OWASP LLM02). Layering both is defense in depth.

## Out of scope (for now)

LLM04 Supply Chain, LLM05 Data and Model Poisoning, LLM06 Unbounded Consumption, and
LLM09 Vector and Embedding Weaknesses (AcmeBot uses keyword retrieval, not a vector store).
