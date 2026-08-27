---
version: v0
date: 2026-08-27
---

# Build report — v0

Course project 0 (coders.su, cohort Dmc-268): a Markdown link checker CLI,
built by an AI agent from a single specification prompt.

## Constraints

Self-imposed on top of the assignment:

- **Minimal empty harness** — [pi agent](https://github.com/badlogic/pi-mono),
  no IDE, no built-in skills;
- **non-frontier model** — `deepseek/deepseek-v4-flash` (reasoning: high, via
  OpenRouter);
- **no LLM help with the spec** — written and fixed by hand only;
- expectation: working version from **one-shot** generation.

## Metrics

| Metric | Value |
|--------|-------|
| Spec size | **861 tokens** ([TokenCount](https://token-count.streamlit.app)) |
| Prompts total | **1** (the spec itself — [prompt log](../prompts/01-generation.md)) |
| Ran on first try | **yes** |
| Auxiliary prompts quality | n/a (none needed) |
| Bugs in result | **1** — cosmetic console table rendering, caused by ambiguous wording in the spec; left unfixed, functionality unaffected |
| Tokens | ↑ 373k in / ↓ 64k out |
| Cost | **$0.138** |
| Tests | 33 passed (every function covered) |

Details and evidence: [llm-usage.md](../llm-usage.md).

## Acceptance (from the spec)

| Gate | Result |
|------|--------|
| `ruff check --fix .` | `All checks passed!`, exit 0 |
| `pytest` | 33 passed, exit 0 |
| `./linckchecker.py --workdir ~/aihome/ecto-1-kb` | green run, exit 0 |

Real-data run: 56 files scanned, 383 links checked, 381 healthy, 2 broken.
Terminal capture: [output-v0.png](../assets/output-v0.png).

## Artifacts

- Specification: [spec-v0.md](../spec/spec-v0.md)
- Prompt chain: [prompts/](../prompts/)
- Token accounting: [llm-usage.md](../llm-usage.md)

## Takeaways

- A tight spec (861 tokens — below every cohort median of 1.2k–2.5k) is enough
  for a one-shot working CLI on a cheap model.
- The single defect traced back to spec wording, not model capability —
  spec precision is the lever, not model size.
