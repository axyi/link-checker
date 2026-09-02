# link-checker — agent rules

Markdown link checker CLI. Course project 0 of the coders-su lab; lab-wide
standards apply (SDD, atomic commits, model sizing, clean-context review).

## Spec

SDD: implementation task → spec first (`docs/spec/spec-vN.md`); the spec is
the contract.

**Spec drift:** architecture/tests/interfaces change → update
`docs/spec/spec-vN.md` same commit.

## Stack

- Python 3.9+, **stdlib only** at runtime (see `requirements.md`)
- Tooling: uv, pytest, ruff; work inside the initialized venv
  (`source .venv/bin/activate`)
- NEVER add dependencies beyond the allowed list without asking.

## Layout

- `linckchecker.py` — the whole implementation (single file, per spec)
- `test_linckchecker.py` — tests; every function has at least one test case
- `docs/` — spec, prompt log, reports, token accounting
- NEVER generate code comments; all program output strictly in English

## go protocol

<!-- SYNC: canonical text lives in standards/workflow.md §9 (lab repo); this copy is intentionally self-contained -->

`go docs/spec/spec-v0.md` = execute that spec end-to-end per its Execution
contract: work from the repo root, create the files its tree lists, follow
its implementation order, run its acceptance gates verbatim, respect its
bounded fix loop, log every prompt to `docs/prompts/`, append tokens/cost to
`docs/llm-usage.md`, finish with its report template (or its blocker
template). On a spec-internal contradiction (two requirements that cannot
both hold), surface the options and stop for a decision — or emit the spec's
blocker template when running unattended; NEVER resolve it silently.

## Commit format

Conventional commits; **one prompt → one commit**, reference the prompt file:
`(prompt: docs/prompts/NN-<slug>.md)`. NEVER mix results of several prompts.
<!-- SYNC: canonical text lives in standards/workflow.md §6 (lab repo); this copy is intentionally self-contained -->

## Branch strategy

`feat/<slug>`, `fix/<slug>`, `docs/<slug>`; parallel agent work via git
worktrees, one worktree per agent — NEVER two agents in one working tree.
Exception: a single-agent run implementing a whole spec end-to-end may
commit directly to `main`.

## Gates — run before reporting success

<!-- DEFAULT STACK (Python/uv). Non-Python: replace this whole block with the project's real commands. -->

```bash
ruff check .                                # → All checks passed!, exit 0
pytest                                      # → exit 0
./linckchecker.py --workdir docs            # → green run on repo docs, exit 0
```

## Review

By the `code-reviewer` subagent (`.claude/agents/code-reviewer.md`) in a clean
context — NEVER self-review in the writing context; deterministic gates
first, LLM review after.

## Reporting

Every prompt → `docs/prompts/`; tokens/cost → `docs/llm-usage.md`; run
reports → `docs/reports/`.

After each run report, generate `docs/reports/tg-post-vN.md` — a
ready-to-paste Telegram post, written in **Russian**: constraints → result →
metrics (executor model — always named; spec tokens, prompts, first-run,
bugs, tokens in/out, cost — when the harness does not expose tokens/cost,
keep that note and add an estimate at public API prices) → a
link to this project's GitHub repository
(https://github.com/axyi/link-checker). Under ~1500 characters.
