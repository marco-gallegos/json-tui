"""Multi-column container for JSON navigation."""

from __future__ import annotations

from dataclasses import dataclass

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer
from textual.message import Message

from json_tui.models import JsonNode
from json_tui.widgets.column import JsonColumn


class ColumnView(ScrollableContainer):
    """Container managing multiple JSON columns with horizontal scrolling."""

    BINDINGS = [
        Binding("left", "focus_left", "Left Column", show=False),
        Binding("right", "focus_right", "Right Column", show=False),
        Binding("h", "focus_left", "Left Column", show=False),
        Binding("l", "focus_right", "Right Column", show=False),
        Binding("enter", "expand", "Expand", show=False),
        Binding("backspace", "collapse", "Collapse", show=False),
        Binding("escape", "collapse", "Collapse", show=False),
    ]

    DEFAULT_CSS = """
    ColumnView {
        width: 100%;
        height: 1fr;
        layout: horizontal;
        overflow-x: auto;
        overflow-y: hidden;
    }

    ColumnView > Horizontal {
        width: auto;
        height: 100%;
    }
    """

    @dataclass
    class NodeSelected(Message):
        """Message when a node is selected in any column."""

        node: JsonNode
        path: list[str]

    def __init__(
        self,
        root: JsonNode,
        name: str | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id)
        self.root = root
        self.columns: list[JsonColumn] = []
        self.active_column_index: int = 0
        self._selected_node: JsonNode | None = None

    def compose(self):
        """Create the initial column layout."""
        with Horizontal():
            if self.root.is_expandable:
                col = JsonColumn(self.root, column_index=0, id="col_0")
                self.columns.append(col)
                yield col

    def on_mount(self) -> None:
        """Focus the first column on mount."""
        if self.columns:
            self.columns[0].focus()

    @on(JsonColumn.Selected)
    def _on_column_selected(self, event: JsonColumn.Selected) -> None:
        """Handle selection in a column."""
        event.stop()
        self._selected_node = event.node
        self._trim_columns_after(event.column.column_index)
        self.post_message(self.NodeSelected(node=event.node, path=event.node.path))

    @on(JsonColumn.Activated)
    def _on_column_activated(self, event: JsonColumn.Activated) -> None:
        """Handle activation (expansion) of a node."""
        event.stop()
        self._expand_node(event.node, event.column.column_index)

    def _expand_node(self, node: JsonNode, from_column: int) -> None:
        """Expand a node by adding a new column."""
        if not node.is_expandable:
            return

        self._trim_columns_after(from_column)

        new_index = from_column + 1
        new_col = JsonColumn(node, column_index=new_index, id=f"col_{new_index}")
        self.columns.append(new_col)

        container = self.query_one(Horizontal)
        container.mount(new_col)

        self.active_column_index = new_index
        new_col.focus()
        self.scroll_end(animate=True)

    def _trim_columns_after(self, index: int) -> None:
        """Remove all columns after the given index."""
        while len(self.columns) > index + 1:
            col = self.columns.pop()
            col.remove()

    def action_focus_left(self) -> None:
        """Focus the column to the left."""
        if self.active_column_index > 0:
            self.active_column_index -= 1
            self.columns[self.active_column_index].focus()

    def action_focus_right(self) -> None:
        """Focus the column to the right or expand current selection."""
        if self.active_column_index < len(self.columns) - 1:
            self.active_column_index += 1
            self.columns[self.active_column_index].focus()
        else:
            self.action_expand()

    def action_expand(self) -> None:
        """Expand the currently selected node."""
        if self.columns and self.active_column_index < len(self.columns):
            col = self.columns[self.active_column_index]
            node = col.get_selected_node()
            if node and node.is_expandable:
                self._expand_node(node, self.active_column_index)

    def action_collapse(self) -> None:
        """Collapse by moving to parent column."""
        if self.active_column_index > 0:
            self._trim_columns_after(self.active_column_index - 1)
            self.active_column_index -= 1
            self.columns[self.active_column_index].focus()

    def get_selected_node(self) -> JsonNode | None:
        """Get the currently selected node."""
        return self._selected_node
