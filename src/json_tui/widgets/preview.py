"""Preview panel for displaying full JSON values."""

from __future__ import annotations

import orjson

from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual.widgets import Static

from json_tui.models import JsonNode
from json_tui.models.json_node import NodeType

MAX_PREVIEW_WIDTH = 2000
LARGE_FIELD_COUNT = 4
MAX_FIELD_COLUMNS = 2


class PreviewPanel(Static):
    """Panel showing the full value of the selected node."""

    DEFAULT_CSS = """
    PreviewPanel {
        width: 100%;
        height: auto;
        min-height: 3;
        max-height: 12;
        padding: 1;
        border: solid $primary-background;
        background: $surface-darken-1;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id)
        self._current_node: JsonNode | None = None

    def update_node(self, node: JsonNode | None) -> None:
        """Update the preview with a new node."""
        self._current_node = node

        if node is None:
            self.update(Text("No selection", style="dim"))
            return

        if node.node_type in (NodeType.OBJECT, NodeType.ARRAY):
            content = self._render_structured(node)
            if content:
                self.update(content)
            else:
                self._render_json_fallback(node)
        else:
            styled = self._style_value(node)
            self.update(styled)

    def _render_structured(self, node: JsonNode) -> Table | None:
        """Try to render as multi-column table."""
        value = node.value
        terminal_width = self.size.width if self.size else 80

        if terminal_width < 40:
            return None

        if node.node_type == NodeType.OBJECT and isinstance(value, dict):
            return self._render_object_table(value, terminal_width)

        if node.node_type == NodeType.ARRAY and isinstance(value, list):
            return self._render_array_table(value, terminal_width)

        return None

    def _render_object_table(self, obj: dict, terminal_width: int) -> Table | None:
        """Render object as multi-column table if large."""
        fields = list(obj.items())
        field_count = len(fields)

        if field_count <= LARGE_FIELD_COUNT:
            return None

        column_count = min(MAX_FIELD_COLUMNS, (terminal_width // 35))
        column_count = max(1, column_count)

        rows_per_column = (field_count + column_count - 1) // column_count

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(no_wrap=True)

        current_row: list[tuple[str, object]] = []

        for key, val in fields:
            current_row.append((key, val))
            if len(current_row) >= rows_per_column:
                self._add_table_row(table, current_row)
                current_row = []

        if current_row:
            self._add_table_row(table, current_row)

        return table if table.row_count > 0 else None

    def _add_table_row(
        self, table: Table, fields: list[tuple[str, object]]
    ) -> None:
        """Add a row to the table with formatted key:value pairs."""
        row_cells = []
        for key, val in fields:
            formatted = self._format_field(key, val)
            row_cells.append(formatted)

        table.add_row("  ".join(row_cells))

    def _format_field(self, key: str, value: object) -> str:
        """Format a single field as key: value."""
        display_value = self._truncate_value(value, max_len=50)
        styled_value = self._style_value_for_display(value, display_value)

        key_str = f"[bold cyan]{key}[/bold cyan]"
        return f"{key_str}: {styled_value}"

    def _render_array_table(self, arr: list, terminal_width: int) -> Table | None:
        """Render array of objects as table if they share keys."""
        if not arr:
            return None

        first_obj = arr[0]
        if not isinstance(first_obj, dict):
            return None

        shared_keys = set(first_obj.keys())

        if not all(isinstance(item, dict) and set(item.keys()) == shared_keys for item in arr):
            return None

        if len(arr) <= 1 and len(shared_keys) <= LARGE_FIELD_COUNT:
            return None

        table = Table(show_header=True, box=None, padding=(0, 1))

        for key in sorted(shared_keys):
            table.add_column(key, no_wrap=False)

        for item in arr[:20]:
            row = []
            for key in sorted(shared_keys):
                val = item.get(key)
                display = self._truncate_value(val, max_len=30)
                styled = self._style_value_for_display(val, display)
                row.append(styled)
            table.add_row(*row)

        if len(arr) > 20:
            table.add_row(*[f"... +{len(arr) - 20} more" for _ in shared_keys])

        return table

    def _render_json_fallback(self, node: JsonNode) -> None:
        """Fallback to JSON syntax rendering."""
        try:
            json_str = orjson.dumps(node.value, option=orjson.OPT_INDENT_2).decode()
            if len(json_str) > MAX_PREVIEW_WIDTH:
                json_str = json_str[:MAX_PREVIEW_WIDTH] + "\n..."
            syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True)
            self.update(syntax)
        except TypeError | ValueError:
            self.update(Text(str(node.value), style="yellow"))

    def _style_value(self, node: JsonNode) -> Text:
        """Create styled text for primitive values."""
        text = Text()

        type_label = node.node_type.value.upper()
        text.append(f"[{type_label}] ", style="dim")

        if node.node_type == NodeType.STRING:
            text.append(f'"{node.value}"', style="green")
        elif node.node_type == NodeType.NUMBER:
            text.append(str(node.value), style="bright_cyan")
        elif node.node_type == NodeType.BOOLEAN:
            text.append("true" if node.value else "false", style="yellow")
        elif node.node_type == NodeType.NULL:
            text.append("null", style="bright_red")
        else:
            text.append(str(node.value))

        return text

    def _truncate_value(self, value: object, max_len: int = 50) -> str:
        """Truncate value for display."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            if len(value) > max_len:
                return value[: max_len - 3] + "..."
            return value
        elif isinstance(value, (dict, list)):
            return f"{type(value).__name__}({len(value)})"
        return str(value)

    def _style_value_for_display(self, value: object, display: str) -> str:
        """Get styled value string for table display."""
        if value is None:
            return f"[dim red]{display}[/dim red]"
        elif isinstance(value, bool):
            return f"[yellow]{display}[/yellow]"
        elif isinstance(value, (int, float)):
            return f"[cyan]{display}[/cyan]"
        elif isinstance(value, str):
            if len(display) > 30:
                return f'"{display}"'
            return f'"[green]{display}[/green]"'
        elif isinstance(value, (dict, list)):
            return f"[dim]{display}[/dim]"
        return display