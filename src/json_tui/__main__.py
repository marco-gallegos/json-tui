"""CLI entry point for JSON TUI."""

from __future__ import annotations

import sys
from pathlib import Path

import click
import orjson

from json_tui.app import JsonTuiApp
from json_tui.logging import setup

LOG_FILE = Path("/tmp/json-tui.log")


@click.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path), required=False)
@click.option(
    "--stdin",
    "-s",
    is_flag=True,
    help="Read JSON from stdin",
)
@click.option(
    "--dev",
    "-d",
    is_flag=True,
    help="Enable dev mode with performance metrics (logs to /tmp/json-tui.log)",
)
@click.version_option(package_name="json-tui")
def main(file: Path | None, stdin: bool, dev: bool) -> None:
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
            json_data = orjson.loads(sys.stdin.read())
        except orjson.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON from stdin: {e}")
    elif file:
        json_path = file
        try:
            with open(file, "rb") as f:
                json_data = orjson.loads(f.read())
        except orjson.JSONDecodeError as e:
            raise click.ClickException(f"Invalid JSON in {file}: {e}")
        except OSError as e:
            raise click.ClickException(f"Cannot read {file}: {e}")
    else:
        raise click.ClickException(
            "No input provided. Pass a JSON file or use --stdin to read from stdin."
        )

    setup(dev, LOG_FILE if dev else None)

    app = JsonTuiApp(json_data=json_data, json_path=json_path)
    app.run()


if __name__ == "__main__":
    main()
