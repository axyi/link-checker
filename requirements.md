# Requirements

## Runtime dependencies

None. `linckchecker.py` uses only the Python standard library
(`argparse`, `concurrent.futures`, `dataclasses`, `pathlib`, `re`,
`urllib`).

## Development dependencies

- `pytest` — test runner
- `ruff` — linter

Both are installed with uv:

```bash
uv add --dev pytest ruff
uv sync
```

Run the checks inside the initialized virtual environment:

```bash
source .venv/bin/activate
ruff check --fix .
pytest
```
