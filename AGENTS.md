# link-checker — agent rules

Markdown link checker CLI. Course project 0 of the coders-su lab; lab-wide
standards apply (SDD, atomic commits, model sizing, clean-context review).

## Stack

- Python 3.9+, **stdlib only** at runtime (see `requirements.md`)
- Tooling: uv, pytest, ruff; work inside the initialized venv
  (`source .venv/bin/activate`)

## Layout

- `linckchecker.py` — the whole implementation (single file, per spec)
- `test_linckchecker.py` — tests; every function has at least one test case
- `docs/` — spec, prompt log, reports, token accounting
- Do not generate code comments; all program output strictly in English

## Commit format

Conventional commits; **one prompt → one commit**, reference the prompt file:
`(prompt: docs/prompts/NN-<slug>.md)`. Never mix results of several prompts.

## Branch strategy

`feat/<slug>`, `fix/<slug>`, `docs/<slug>`; parallel agent work via git
worktrees, one worktree per agent.

## Gates — run before reporting success

```bash
ruff check .                                # → All checks passed!, exit 0
pytest                                      # → exit 0
./linckchecker.py --workdir docs            # → green run on repo docs, exit 0
```

## Review

By the `code-reviewer` subagent (`.claude/agents/code-reviewer.md`) in a clean
context; deterministic gates first, LLM review after.

## Reporting

Every prompt → `docs/prompts/`; tokens/cost → `docs/llm-usage.md`; run
reports → `docs/reports/`.

After each run report, generate `docs/reports/tg-post-vN.md` — a
ready-to-paste Telegram post, written in **Russian**: constraints → result →
metrics (spec tokens, prompts, first-run, bugs, tokens in/out, cost) → a
link to this project's GitHub repository
(https://github.com/axyi/link-checker). Under ~1500 characters.
