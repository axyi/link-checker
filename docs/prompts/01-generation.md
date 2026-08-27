---
date: 2026-08-27
model: deepseek/deepseek-v4-flash (reasoning: high, via OpenRouter)
harness: pi (minimal empty harness)
stage: generation
tokens_in: 373000
tokens_out: 64000
cost_usd: 0.138
---

# Prompt 01 — one-shot generation

The only prompt sent to the LLM in this project. Its full text is the
specification, passed verbatim: [`../spec/spec-v0.md`](../spec/spec-v0.md)
(861 tokens).

Self-imposed constraints for this run:

- minimal empty harness (pi agent) — no IDE integration, no built-in skills;
- deliberately non-frontier model (deepseek-v4-flash);
- no LLM assistance for writing or fixing the specification;
- expectation: a working version from one-shot generation.

Result: working code on the first run; no auxiliary prompts were needed.
