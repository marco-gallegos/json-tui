# AGENTS.md - Development Guide for json-tui

## Project Overview

- **Project**: json-tui - A terminal JSON viewer with columnar navigation
- **Python**: 3.14+
- **Package Manager**: uv
- **UI Framework**: Textual (TUI)
- **CLI Framework**: Click

## Build, Run & Development Commands

```bash
# Install dependencies
uv sync

# Run in development mode
uv run json-tui <file.json>

# Install in editable mode
uv pip install -e .

# Run with stdin
echo '{"key": "value"}' | uv run json-tui --stdin
```

### Testing

**No test framework is currently configured.** When adding tests:

```bash
# If using pytest (add with: uv add --dev pytest)
uv run pytest                           # Run all tests
uv run pytest path/to/test.py           # Run specific file
uv run pytest -k test_name              # Run tests matching pattern
uv run pytest -v                         # Verbose output
```

### Linting & Type Checking

```bash
# Install ruff if needed: uv add --dev ruff
uv run ruff check src/      # Linter
uv run ruff format src/     # Formatter
uv run mypy src/            # Type checking (if installed)
```

### Adding Dependencies

```bash
uv add <package>           # Production
uv add --dev <package>    # Development
```

## Code Style Guidelines

### Imports

```python
# Order: stdlib → third-party → local
from __future__ import annotations

import json
from pathlib import Path

import click
from textual import on
from textual.app import App

from json_tui.models import JsonNode
from json_tui.widgets import ColumnView
```

### Type Hints

- Use modern Python 3.10+ union syntax: `Path | None` (not `Optional[Path]`)
- Use `from __future__ import annotations` for deferred evaluation
- Type all function parameters and return values

### Naming Conventions

- **Classes**: PascalCase (`JsonTuiApp`, `JsonNode`)
- **Functions/variables**: snake_case (`json_data`, `_load_file`)
- **Private methods**: prefix with underscore (`_load_file`)
- **Files**: snake_case (`json_node.py`)

### Docstrings

- Use triple quotes `"""..."""` for all docstrings
- One-line summary for public methods

### Error Handling

- Use `click.ClickException` for CLI errors
- Use Textual's notification system for runtime errors:
  ```python
  self.notify(f"Error: {e}", severity="error")
  ```
- Catch specific exceptions, avoid bare `except:`

### Textual Widget Patterns

```python
class JsonColumn(OptionList):
    """A column displaying keys at one level of the JSON tree."""

    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=False),
    ]

    DEFAULT_CSS = """
    JsonColumn {
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        ...

    @on(OptionList.OptionHighlighted)
    def _on_highlight(self, event: OptionList.OptionHighlighted) -> None:
        event.stop()
        ...
```

### Message/Event Patterns

- Use Textual's Message system for inter-widget communication
- Define messages as nested dataclasses with `Message` base class
- Stop propagation with `event.stop()`

```python
class Selected(Message):
    node: JsonNode
    column: JsonColumn
```

## Project Structure

```
src/json_tui/
├── __init__.py         # Package init, version
├── __main__.py         # CLI entry point (Click)
├── app.py              # Main JsonTuiApp
├── models/
│   ├── __init__.py
│   └── json_node.py    # JsonNode dataclass, NodeType enum
└── widgets/
    ├── __init__.py
    ├── column.py        # JsonColumn widget
    ├── column_view.py  # ColumnView container
    └── preview.py      # PreviewPanel widget
```

## Common Tasks

```bash
# Run app
uv run json-tui sample.json

# Debug with Textual dev mode
uv run textual run src/json_tui/__main__.py
```
