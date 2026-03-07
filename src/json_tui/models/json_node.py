"""JSON tree node representation for navigation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    """Type of JSON node."""

    OBJECT = "object"
    ARRAY = "array"
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    NULL = "null"


@dataclass
class JsonNode:
    """Represents a node in the JSON tree structure."""

    key: str
    value: Any
    node_type: NodeType
    parent: JsonNode | None = None
    children: list[JsonNode] = field(default_factory=list)
    depth: int = 0

    @classmethod
    def from_json(
        cls, data: Any, key: str = "root", parent: JsonNode | None = None, depth: int = 0
    ) -> JsonNode:
        """Build a JsonNode tree from parsed JSON data."""
        node_type = cls._get_type(data)
        node = cls(
            key=key,
            value=data,
            node_type=node_type,
            parent=parent,
            depth=depth,
        )

        if isinstance(data, dict):
            for k, v in data.items():
                child = cls.from_json(v, key=k, parent=node, depth=depth + 1)
                node.children.append(child)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                child = cls.from_json(item, key=f"[{i}]", parent=node, depth=depth + 1)
                node.children.append(child)

        return node

    @staticmethod
    def _get_type(value: Any) -> NodeType:
        """Determine the NodeType for a value."""
        if isinstance(value, dict):
            return NodeType.OBJECT
        elif isinstance(value, list):
            return NodeType.ARRAY
        elif isinstance(value, str):
            return NodeType.STRING
        elif isinstance(value, bool):
            return NodeType.BOOLEAN
        elif isinstance(value, int | float):
            return NodeType.NUMBER
        elif value is None:
            return NodeType.NULL
        return NodeType.STRING

    @property
    def is_expandable(self) -> bool:
        """Check if this node can be expanded (has children)."""
        return self.node_type in (NodeType.OBJECT, NodeType.ARRAY) and len(self.children) > 0

    @property
    def display_key(self) -> str:
        """Get the display string for the key."""
        return self.key

    @property
    def display_value(self) -> str:
        """Get a short display string for the value."""
        if self.node_type == NodeType.OBJECT:
            return f"{{ {len(self.children)} keys }}"
        elif self.node_type == NodeType.ARRAY:
            return f"[ {len(self.children)} items ]"
        elif self.node_type == NodeType.STRING:
            val = str(self.value)
            if len(val) > 50:
                return f'"{val[:47]}..."'
            return f'"{val}"'
        elif self.node_type == NodeType.NULL:
            return "null"
        elif self.node_type == NodeType.BOOLEAN:
            return "true" if self.value else "false"
        return str(self.value)

    @property
    def path(self) -> list[str]:
        """Get the full path from root to this node."""
        parts = []
        node: JsonNode | None = self
        while node is not None:
            parts.append(node.key)
            node = node.parent
        return list(reversed(parts))

    @property
    def path_string(self) -> str:
        """Get the path as a dot-separated string."""
        return " › ".join(self.path)

    def get_child(self, index: int) -> JsonNode | None:
        """Get a child by index."""
        if 0 <= index < len(self.children):
            return self.children[index]
        return None
