# Contributing

## Development Setup

```bash
cd aweshelf
uv venv
uv pip install -e .
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Architecture

```
src/aweshelf/
  __init__.py      # Version
  types.py         # Bookmark dataclass
  cli.py           # Click entry point
  commands/        # One file per command
  lib/             # Pure business logic
  tui/             # textual app
```

- `lib/` has no CLI coupling — pure functions, testable in isolation
- `commands/` are thin orchestrators calling `lib/` functions
- `tui/` reads from `lib/store`, does not write

## Code Style

- Python 3.10+, type hints throughout
- `click` for CLI, `textual` for TUI
- `unittest` for tests
- Functions: `snake_case`, Types: `PascalCase`, Constants: `UPPER_CASE`
- Error messages are user-facing and actionable
