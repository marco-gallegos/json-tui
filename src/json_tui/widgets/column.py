"""Single column widget for displaying one level of JSON."""

from __future__ import annotations

from dataclasses import dataclass

from rich.style import Style
from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from json_tui.models import JsonNode


class JsonColumn(OptionList):
    """A column displaying keys/indices at one level of the JSON tree."""

    BINDINGS = [
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("j", "cursor_down", "Down", show=False),
    ]

    DEFAULT_CSS = """
    JsonColumn {
        width: 1fr;
        min-width: 20;
        max-width: 40;
        height: 100%;
        border: solid $primary-background;
        background: $surface;
    }

    JsonColumn:focus {
        border: solid $accent;
    }

    JsonColumn > .option-list--option-highlighted {
        background: $accent;
        color: $text;
    }
    """

    @dataclass
    class Selected(Message):
        """Message sent when a node is selected."""

        node: JsonNode
        column: JsonColumn

    @dataclass
    class Activated(Message):
        """Message sent when user presses enter to expand a node."""

        node: JsonNode
        column: JsonColumn

    def __init__(
        self,
        node: JsonNode,
        column_index: int,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id)
        self.node = node
        self.column_index = column_index
        self._node_map: dict[str, JsonNode] = {}

    def compose(self):
        """No child widgets needed - we use add_options instead."""
        return []

    def on_mount(self) -> None:
        """Populate options when mounted."""
        self._populate_options()

    def _populate_options(self) -> None:
        """Fill the column with options from the node's children."""
        self.clear_options()
        self._node_map.clear()

        for i, child in enumerate(self.node.children):
            option_id = f"node_{i}"
            self._node_map[option_id] = child

            label = self._make_label(child)
            self.add_option(Option(label, id=option_id))

    def _make_label(self, node: JsonNode) -> Text:
        """Create a styled label for a node."""
        text = Text()

        if node.is_expandable:
            text.append("▸ ", style=Style(color="cyan"))
        else:
            text.append("  ")

        text.append(node.display_key, style=self._key_style(node))
        text.append(" ")
        text.append(node.display_value, style=self._value_style(node))

        return text

    def _key_style(self, node: JsonNode) -> Style:
        """Get the style for a key based on node type."""
        if node.key.startswith("["):
            return Style(color="bright_magenta")
        return Style(color="bright_white", bold=True)

    def _value_style(self, node: JsonNode) -> Style:
        """Get the style for a value based on node type."""
        from json_tui.models.json_node import NodeType

        styles = {
            NodeType.OBJECT: Style(color="bright_black"),
            NodeType.ARRAY: Style(color="bright_black"),
            NodeType.STRING: Style(color="green"),
            NodeType.NUMBER: Style(color="bright_cyan"),
            NodeType.BOOLEAN: Style(color="yellow"),
            NodeType.NULL: Style(color="bright_red"),
        }
        return styles.get(node.node_type, Style())

    def get_selected_node(self) -> JsonNode | None:
        """Get the currently highlighted node."""
        if self.highlighted is not None:
            option = self.get_option_at_index(self.highlighted)
            if option and option.id:
                return self._node_map.get(option.id)
        return None

    @on(OptionList.OptionHighlighted)
    def _on_highlight(self, event: OptionList.OptionHighlighted) -> None:
        """Handle option highlight changes."""
        event.stop()
        node = self.get_selected_node()
        if node:
            self.post_message(self.Selected(node=node, column=self))

    @on(OptionList.OptionSelected)
    def _on_select(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection (enter key)."""
        event.stop()
        node = self.get_selected_node()
        if node and node.is_expandable:
            self.post_message(self.Activated(node=node, column=self))

    def select_index(self, index: int) -> None:
        """Select an option by index."""
        if 0 <= index < self.option_count:
            self.highlighted = index
