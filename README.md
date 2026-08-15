# Markdown Link & Dead Code Checker

A zero-dependency Python CLI that recursively scans Markdown files, extracts
all links, verifies that each resource is reachable, and prints a table of
broken links with summary statistics.

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

## Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (dependency management)
- Development only: `pytest`, `ruff` (see [requirements.md](requirements.md))

## Setup

```bash
uv add --dev pytest ruff
uv sync
source .venv/bin/activate
```

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

## Testing

Every function in `linckchecker.py` is covered by at least one test case in
[test_linckchecker.py](test_linckchecker.py) (33 tests). HTTP behavior is
exercised against a local test server, so the suite requires no network.

```bash
source .venv/bin/activate
pytest
```

## Acceptance results

| Check | Result |
| --- | --- |
| `ruff check --fix .` | `All checks passed!` (exit 0) |
| `pytest` | `33 passed` (exit 0) |
| `./linckchecker.py --workdir ~/aihome/ecto-1-kb` | Green run (exit 0) |
