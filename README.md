# Markdown Link & Dead Code Checker

![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![Zero runtime deps](https://img.shields.io/badge/runtime%20deps-none-brightgreen)
![Tests](https://img.shields.io/badge/tests-33%20passed-brightgreen)
![AI-built](https://img.shields.io/badge/AI--built-one--shot%2C%20%240.138-8A2BE2)

A zero-dependency Python CLI that recursively scans Markdown files, extracts
all links, verifies that each resource is reachable, and prints a table of
broken links with summary statistics.

Built by an AI agent from a single 861-token specification — one prompt, one
shot, on a non-frontier model. See the [build report](docs/reports/report-v0.md).

## Features

- Recursively scans every `.md` file under `--workdir` (default: current directory)
- Extracts two link forms:
  - Markdown links: `[text](url)` (space between `]` and `(` is tolerated)
  - Bare `file:///...` URLs
- Checks each resource:
  - `http://` / `https://` links via an HTTP `HEAD` request with a configurable
    timeout; `3xx` responses are followed (up to 10 hops) to obtain the final
    status; a link is healthy only when the final status is `200`
  - File links (relative paths, `file://`, symlinks) via existence check;
    relative paths resolve against the directory of the Markdown file where
    the link was found; missing files are reported with status `n/a`
  - Fragment-only (`#anchor`) and non-http schemes (`mailto:`, ...) are
    treated as healthy
- Concurrent link checking (configurable worker count) with deterministic output
- Markdown table of broken links followed by summary statistics
- Pure Python standard library — no runtime dependencies

## Usage

```bash
./linckchecker.py --workdir ./docs
```

| Option        | Default | Description                              |
|---------------|---------|------------------------------------------|
| `--workdir`   | `./`    | Directory to scan for `.md` files        |
| `--timeout`   | `10`    | HTTP request timeout in seconds          |
| `--workers`   | `10`    | Number of parallel link checks           |

### Output

Broken links are printed as a Markdown table, sorted by source file and line:

```
| Link Text | Link | Source File | Status |
|---|---|---|---|
| Дизайн | https://www.figma.com/design/... | README.md:3 | 404 |
```

When every link is healthy the tool prints `No broken links found.` instead.
Summary statistics follow the table:

```
Total links checked: 383
Total files scanned: 56
Healthy: 381
Broken: 2
```

Exit code is `0` on success; `1` is returned when `--workdir` does not exist.

## Setup

Requires Python 3.9+ and [uv](https://docs.astral.sh/uv/); development-only
dependencies are `pytest` and `ruff` (see [requirements.md](requirements.md)).

```bash
uv add --dev pytest ruff
uv sync
source .venv/bin/activate
```

## Testing

Every function in `linckchecker.py` is covered by at least one test case in
[test_linckchecker.py](test_linckchecker.py) (33 tests). HTTP behavior is
exercised against a local test server, so the suite requires no network.

```bash
source .venv/bin/activate
pytest
```

## Build report

This is project 0 of an AI-driven development course — the point is not the
tool, but the process: spec-driven development on a minimal harness
([pi](https://github.com/badlogic/pi-mono)) with a cheap model
(`deepseek/deepseek-v4-flash`) and full cost accounting.

**Headline:** 861-token spec · 1 prompt · first run green · 1 cosmetic bug ·
↑373k/↓64k tokens · **$0.138**.

- [Build report](docs/reports/report-v0.md) — constraints, metrics, acceptance
- [Specification](docs/spec/spec-v0.md) — the single prompt that produced the code
- [Prompt chain](docs/prompts/) · [LLM usage](docs/llm-usage.md)
