# JSON TUI

A terminal JSON viewer with columnar navigation, inspired by [JSON Hero](https://jsonhero.io).

![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)

## Why?

I love json hero but IRL privacy is a serious deal, in some companies
i worked leaked client data can make you unemployed or worst.

On my every day json unreadable responses (very long) happens a lot so
this viewer gives me a similar experience without any data leak risk.

what's solving?

- offline, no data sent to any server
- terminal-based, no need for a browser or GUI (work on ssh or inside pods/containers)
- python-based, easy to install and extend
- performance,use python means i can extend it with rust for performance critical
parts if needed
- uv compatibility, can be easily installed and run with uv

## Features

- **Columnar Navigation**: Navigate nested JSON structures in a multi-column view
- **Keyboard-driven**: Vim-style keybindings (hjkl) and arrow keys
- **Syntax Highlighting**: Color-coded values by type (strings, numbers, booleans, null)
- **Live Preview**: See full values in the preview panel
- **Path Breadcrumbs**: Always know where you are in the structure
- **Stdin Support**: Pipe JSON directly from curl or other commands

## Installation

```bash
# Easy with uv
uv tool install json-tui

# Also pip works
pip install json-tui

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
| ----- | -------- |
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
json-tui examples/sample.json
```

## Next Steps

- parse json using rust for better performance or py threads
- improve long columns handling
- fuzzy search
- copy curent value/node to clipboard

## License

MIT
