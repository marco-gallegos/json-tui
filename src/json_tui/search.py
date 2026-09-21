"""Fuzzy search over the JSON node tree."""

from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz, process

from json_tui.models import JsonNode
from json_tui.models.json_node import NodeType


@dataclass(frozen=True)
class SearchEntry:
    """A single searchable node in the JSON tree."""

    node: JsonNode
    depth: int
    text: str

    @property
    def path_string(self) -> str:
        """Dot-separated path used for display."""
        return self.node.path_string


@dataclass(frozen=True)
class SearchResult:
    """A matched node with its relevance score."""

    entry: SearchEntry
    score: int

    @property
    def node(self) -> JsonNode:
        return self.entry.node


def build_index(root: JsonNode) -> list[SearchEntry]:
    """Walk the tree and build a flat list of searchable entries."""
    entries: list[SearchEntry] = []
    _collect(root, 0, entries)
    return entries


def _collect(node: JsonNode, depth: int, entries: list[SearchEntry]) -> None:
    entries.append(SearchEntry(node=node, depth=depth, text=_node_search_text(node)))
    for child in node.children:
        _collect(child, depth + 1, entries)


def _node_search_text(node: JsonNode) -> str:
    """Build a lowercased searchable text blob for a single node."""
    parts: list[str] = [node.key, node.path_string]

    if node.node_type in (
        NodeType.STRING,
        NodeType.NUMBER,
        NodeType.BOOLEAN,
        NodeType.NULL,
    ):
        parts.append(str(node.value))

    return "\n".join(parts).lower()


MAX_CANDIDATES = 500

POST_FILTER_LIMIT = 50


def fuzzy_search(
    query: str,
    entries: list[SearchEntry],
    limit: int = POST_FILTER_LIMIT,
    threshold: int = 30,
) -> list[SearchResult]:
    """Return entries fuzzy-matched against the query, best scored first.

    All entries are similarity-scored at C speed (rapidfuzz), the top
    candidates are kept, then filtered so every whitespace-separated token
    appears as a subsequence of the entry text before being returned.
    """
    query = query.strip()
    if not query or not entries:
        return []

    tokens = [token.lower() for token in query.split()]

    matches = process.extract(
        query,
        [entry.text for entry in entries],
        scorer=fuzz.partial_ratio,
        limit=MAX_CANDIDATES,
        score_cutoff=threshold,
    )

    candidates = [
        (entries[index], score)
        for choice, score, index in matches
        if all(_is_subsequence(choice, token) for token in tokens)
    ]
    candidates.sort(key=lambda item: (item[1], item[0].depth), reverse=True)

    return [
        SearchResult(entry=entry, score=score) for entry, score in candidates[:limit]
    ]


def _is_subsequence(haystack: str, needle: str) -> bool:
    """True if every char of needle appears in haystack in order."""
    it = iter(haystack)
    return all(char in it for char in needle)
