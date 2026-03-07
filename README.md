# JSON TUI

A terminal JSON viewer with columnar navigation, inspired by [JSON Hero](https://jsonhero.io).

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)

## Features

- **Columnar Navigation**: Navigate nested JSON structures in a multi-column view
- **Keyboard-driven**: Vim-style keybindings (hjkl) and arrow keys
- **Syntax Highlighting**: Color-coded values by type (strings, numbers, booleans, null)
- **Live Preview**: See full values in the preview panel
- **Path Breadcrumbs**: Always know where you are in the structure
- **Stdin Support**: Pipe JSON directly from curl or other commands

## Installation

```bash
# Clone and install with uv
git clone <repo>
cd json_tui
uv sync

# Or install in development mode
uv pip install -e .
```

## Usage

```bash
# View a JSON file
json-tui data.json

# Pipe from stdin
curl https://api.example.com/data | json-tui --stdin

# Or use echo
echo '{"hello": "world", "nested": {"key": "value"}}' | json-tui -s
```

## Keybindings

| Key | Action |
|-----|--------|
| `↑` / `k` | Move up in current column |
| `↓` / `j` | Move down in current column |
| `←` / `h` | Focus previous column |
| `→` / `l` | Focus next column / expand |
| `Enter` | Expand selected node |
| `Backspace` / `Esc` | Collapse / go back |
| `?` | Show help |
| `q` | Quit |

## Development

```bash
# Run directly with uv
uv run json-tui sample.json

# Or activate the venv
source .venv/bin/activate
json-tui sample.json
```

## License

MIT
