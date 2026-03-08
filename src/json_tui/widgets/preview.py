"""Preview panel for displaying full JSON values."""

from __future__ import annotations

import orjson

from rich.syntax import Syntax
from rich.text import Text
from textual.widgets import Static

from json_tui.models import JsonNode
from json_tui.models.json_node import NodeType


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
            try:
                json_str = orjson.dumps(node.value, option=orjson.OPT_INDENT_2).decode()
                if len(json_str) > 2000:
                    json_str = json_str[:2000] + "\n..."
                syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True)
                self.update(syntax)
            except TypeError, ValueError:
                self.update(Text(str(node.value), style="yellow"))
        else:
            styled = self._style_value(node)
            self.update(styled)

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
