# JSON TUI

A terminal JSON viewer with columnar navigation, inspired by [JSON Hero](https://jsonhero.io).

![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)

## Why?

I love JSON Hero, but in real life, privacy is a serious issue. In some companies
I've worked at, leaked client data can get you fired or worse.
In my everyday work, unreadable JSON responses (very long ones) happen frequently,
so this viewer gives me a similar experience without any data leak risk.

### What's it solving?

- **Offline** - no data sent to any server
- **Terminal-based** - no need for a browser or GUI (works over SSH or inside pods/containers)
- **Python-based** - easy to install and extend
- **Performance** - using Python means I can extend it with Rust for performance-critical parts if needed
- **UV compatibility** - can be easily installed and run with UV

## Features

- **Columnar Navigation**: Navigate nested JSON structures in a multi-column view
- **Keyboard-driven**: Vim-style keybindings (hjkl) and arrow keys
- **Syntax Highlighting**: Color-coded values by type (strings, numbers, booleans, null)
- **Live Preview**: See full values in the preview panel
- **Path Breadcrumbs**: Always know where you are in the structure
- **Stdin Support**: Pipe JSON directly from curl or other commands

## Installation

```bash
# Easy with UV
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
# Run directly with UV
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
