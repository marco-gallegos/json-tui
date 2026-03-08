"""CLI entry point for JSON TUI."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from json_tui.app import JsonTuiApp


@click.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    "--stdin",
    "-s",
    is_flag=True,
    help="Read JSON from stdin",
)
@click.version_option(package_name="json-tui")
def main(file: Path | None, stdin: bool) -> None:
    """A terminal JSON viewer with columnar navigation.

    Navigate JSON files with arrow keys in a column-based interface,
    similar to JSON Hero but in your terminal.


    \b
    Examples:
        json-tui data.json
        curl api.example.com/data | json-tui --stdin
        echo '{"hello": "world"}' | json-tui -s

    By: Marco Gallegos
    """
    json_data = None
    json_path = None

    if stdin or (not file and not sys.stdin.isatty()):
        try:
            json_data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON from stdin: {e}")
    elif file:
        json_path = file
        try:
            with open(file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON in {file}: {e}")
        except OSError as e:
            raise click.ClickException(f"Cannot read {file}: {e}")
    else:
        raise click.ClickException(
            "No input provided. Pass a JSON file or use --stdin to read from stdin."
        )

    app = JsonTuiApp(json_data=json_data, json_path=json_path)
    app.run()


if __name__ == "__main__":
    main()
