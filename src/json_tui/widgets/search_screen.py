"""Modal screen for fuzzy searching across the JSON tree."""

from __future__ import annotations

from functools import partial

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.timer import Timer
from textual.widgets import Input, Label, ListItem, ListView

from json_tui.search import SearchEntry, SearchResult, fuzzy_search

_SEARCH_CSS = """
SearchScreen {
    align: center middle;
    background: rgba(0, 0, 0, 0.6);
}

#search-box {
    width: 70%;
    max-width: 120;
    height: 60%;
    max-height: 40;
    border: thick $accent;
    background: $background;
    padding: 1;
}

#search-input {
    width: 100%;
    margin-bottom: 1;
}

#search-results {
    width: 100%;
    height: 1fr;
}

#search-results .result-path {
    color: $text-muted;
    text-style: italic;
}

#search-results .result-value {
    color: $text;
}
"""


class SearchScreen(ModalScreen[SearchResult | None]):
    """Search screen that fuzzy-matches over the whole JSON tree."""

    DEFAULT_CSS = _SEARCH_CSS

    BINDINGS = [
        ("escape", "dismiss_search", "Close"),
        ("down", "focus_results", "Results"),
    ]

    SEARCH_DEBOUNCE_S = 0.15

    def __init__(self, entries: list[SearchEntry]) -> None:
        super().__init__()
        self.entries = entries
        self._results: list[SearchResult] = []
        self._debounce_timer: Timer | None = None
        self._generation = 0

    def compose(self) -> ComposeResult:
        """Build the search layout."""
        with Vertical(id="search-box"):
            yield Input(placeholder="Search JSON…", id="search-input")
            yield ListView(id="search-results")

    def on_mount(self) -> None:
        """Focus the input on open."""
        self.query_one("#search-input", Input).focus()

    def action_dismiss_search(self) -> None:
        """Dismiss the screen without a result."""
        self.dismiss(None)

    def action_choose(self) -> None:
        """Select the top (or highlighted) result."""
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        if not self._results:
            return
        list_view = self.query_one("#search-results", ListView)
        index = list_view.index if list_view.index is not None else 0
        if 0 <= index < len(self._results):
            self.dismiss(self._results[index])

    def action_focus_results(self) -> None:
        """Focus the results list for keyboard navigation."""
        list_view = self.query_one("#search-results", ListView)
        if list_view.index is None and list_view.children:
            list_view.index = 0
        list_view.focus()

    @on(Input.Changed)
    def _on_query_changed(self, event: Input.Changed) -> None:
        """Debounce the search as the query changes."""
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        self._debounce_timer = self.set_timer(
            self.SEARCH_DEBOUNCE_S,
            partial(self._refresh_results, event.value),
        )

    async def _refresh_results(self, query: str) -> None:
        """Run the search and rebuild the results list."""
        self._generation += 1
        generation = self._generation

        self._results = fuzzy_search(query, self.entries)
        list_view = self.query_one("#search-results", ListView)
        list_view.index = None

        await list_view.clear()
        if generation != self._generation:
            return

        await list_view.extend(self._make_items(self._results))
        if self._results:
            list_view.index = 0

    def _make_items(self, results: list[SearchResult]) -> list[ListItem]:
        """Create ListItems for the given results."""
        items = []
        for result in results:
            node = result.node
            label_path = Label(
                f"[dim]{result.entry.path_string}[/dim]",
                classes="result-path",
            )
            label_value = Label(str(node.display_value), classes="result-value")
            items.append(ListItem(label_path, label_value))
        return items

    @on(Input.Submitted)
    def _on_input_submitted(self) -> None:
        """Choose the top result when Enter is pressed in the input."""
        self.action_choose()

    @on(ListView.Selected)
    def _on_result_selected(self, event: ListView.Selected) -> None:
        """Dismiss the screen with the selected match."""
        event.stop()
        if event.index is not None and 0 <= event.index < len(self._results):
            self.dismiss(self._results[event.index])
