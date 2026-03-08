"""Main Textual application for JSON TUI."""

from __future__ import annotations

from pathlib import Path

import orjson
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Static

from json_tui.models import JsonNode
from json_tui.widgets import ColumnView, PreviewPanel
from json_tui.logging import logger, timeit


def _count_nodes(node: JsonNode) -> tuple[int, int]:
    """Count total nodes and max depth."""
    count = 1
    max_depth = node.depth

    for child in node.children:
        child_count, child_depth = _count_nodes(child)
        count += child_count
        max_depth = max(max_depth, child_depth)

    return count, max_depth


class PathDisplay(Static):
    """Widget showing the current path in the JSON tree."""

    DEFAULT_CSS = """
    PathDisplay {
        width: 100%;
        height: 1;
        padding: 0 1;
        background: $primary-background;
        color: $text-muted;
    }
    """

    def update_path(self, path: list[str]) -> None:
        """Update the displayed path."""
        path_str = " › ".join(path) if path else "root"
        self.update(f"📍 {path_str}")


class JsonTuiApp(App):
    """A terminal JSON viewer with columnar navigation."""

    TITLE = "JSON TUI"
    SUB_TITLE = "Navigate JSON like a pro"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "toggle_help", "Help"),
    ]

    CSS = """
    Screen {
        background: $background;
    }

    #main-container {
        width: 100%;
        height: 100%;
    }

    #content {
        width: 100%;
        height: 1fr;
    }

    #bottom-panel {
        width: 100%;
        height: auto;
        dock: bottom;
    }
    """

    def __init__(
        self,
        json_data: dict | list | None = None,
        json_path: Path | None = None,
    ) -> None:
        super().__init__()
        self.json_data = json_data
        self.json_path = json_path
        self.root_node: JsonNode | None = None

    def compose(self) -> ComposeResult:
        """Create the app layout."""
        yield Header()

        with Vertical(id="main-container"):
            yield PathDisplay(id="path-display")

            with Container(id="content"):
                if self.root_node and self.root_node.is_expandable:
                    yield ColumnView(self.root_node, id="column-view")
                else:
                    yield Static(
                        "No JSON data loaded or data is not expandable",
                        id="empty-message",
                    )

            with Container(id="bottom-panel"):
                yield PreviewPanel(id="preview")

        yield Footer()

    def on_mount(self) -> None:
        """Load JSON data on mount."""
        if self.json_path:
            self._load_file(self.json_path)
        elif self.json_data:
            self._load_data(self.json_data)

        if self.json_path:
            self.sub_title = str(self.json_path.name)

    @timeit("File loaded & parsed")
    def _load_file(self, path: Path) -> None:
        """Load JSON from a file."""
        try:
            file_size = path.stat().st_size

            with open(path, "rb") as f:
                data = orjson.loads(f.read())
            self._load_data(data)

            if self.root_node:
                node_count, max_depth = _count_nodes(self.root_node)
                logger.debug(
                    f"file={path.name} size={file_size} nodes={node_count} depth={max_depth}"
                )
        except (orjson.JSONDecodeError, OSError) as e:
            self.notify(f"Error loading file: {e}", severity="error")

    @timeit("JSON data loaded to tree")
    def _load_data(self, data: dict | list) -> None:
        """Load parsed JSON data."""
        self.json_data = data
        self.root_node = JsonNode.from_json(data)

        if self.is_mounted:
            self._refresh_view()

    @timeit("View refreshed")
    def _refresh_view(self) -> None:
        """Refresh the column view with new data."""
        content = self.query_one("#content", Container)

        for child in list(content.children):
            child.remove()

        if self.root_node and self.root_node.is_expandable:
            column_view = ColumnView(self.root_node, id="column-view")
            content.mount(column_view)
        else:
            content.mount(Static("No expandable data", id="empty-message"))

    @on(ColumnView.NodeSelected)
    def _on_node_selected(self, event: ColumnView.NodeSelected) -> None:
        """Handle node selection."""
        event.stop()

        path_display = self.query_one("#path-display", PathDisplay)
        path_display.update_path(event.path)

        preview = self.query_one("#preview", PreviewPanel)
        preview.update_node(event.node)

    def action_toggle_help(self) -> None:
        """Show help information."""
        self.notify(
            "↑↓/jk: Navigate | ←→/hl: Columns | Enter: Expand | Backspace: Collapse | q: Quit",
            timeout=5,
        )
