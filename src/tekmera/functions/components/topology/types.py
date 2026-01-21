"""Data structures for topology representation.

Defines the graph data structures used for blueprint topology analysis.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ...meta.types import Platform


class EdgeType(Enum):
    """Types of edges in the topology graph."""

    NORMAL = "normal"  # Standard module-to-module flow
    ROUTER_BRANCH = "router_branch"  # Router branch path
    ERROR_HANDLER = "error_handler"  # Error handling path
    CONDITIONAL = "conditional"  # Conditional flow with filter


@dataclass
class GraphPosition:
    """Position information for a node in the graph."""

    depth: int = 0  # Distance from entry points
    path: str = "main"  # Path identifier (main, branch_1, error_path, etc.)
    order: int = 0  # Order within the path
    parent_id: Optional[str] = None  # Parent node ID if in nested flow


@dataclass
class TopologyNode:
    """A node in the topology graph representing a blueprint module."""

    id: str
    module_type: str
    name: str
    platform: Platform
    raw_data: Dict[str, Any]
    position: GraphPosition = field(default_factory=GraphPosition)

    def __post_init__(self):
        """Validate node data after initialization."""
        if not self.id:
            raise ValueError("Node ID cannot be empty")
        if not self.module_type:
            raise ValueError("Node module_type cannot be empty")

    @property
    def is_trigger(self) -> bool:
        """Check if this node is a trigger."""
        return "trigger" in self.module_type.lower() or "watch" in self.module_type.lower()

    @property
    def is_router(self) -> bool:
        """Check if this node is a router."""
        return "router" in self.module_type.lower()

    @property
    def is_filter(self) -> bool:
        """Check if this node is a filter."""
        return self.raw_data.__contains__("filter")

    @property
    def is_error_handler(self) -> bool:
        """Check if this node is an error handler."""
        return "error" in self.module_type.lower() or "onerror" in self.module_type.lower()


@dataclass
class TopologyEdge:
    """An edge in the topology graph representing flow between modules."""

    source: str
    target: str
    edge_type: EdgeType = EdgeType.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate edge data after initialization."""
        if not self.source or not self.target:
            raise ValueError("Edge source and target cannot be empty")
        if self.source == self.target:
            raise ValueError("Edge cannot connect a node to itself")


@dataclass
class TopologyGraph:
    """Complete topology graph for a blueprint."""

    nodes: List[TopologyNode] = field(default_factory=list)
    edges: List[TopologyEdge] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)  # Node IDs that are entry points
    platform: Platform = Platform.WORKFRONT_FUSION

    def __post_init__(self):
        """Validate graph consistency after initialization."""
        self._validate_graph()

    def _validate_graph(self):
        """Validate the graph structure for consistency."""
        # Check for duplicate node IDs
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Duplicate node IDs found in graph")

        # Check that all edge endpoints reference existing nodes
        valid_node_ids = set(node_ids)
        for edge in self.edges:
            if edge.source not in valid_node_ids:
                raise ValueError(f"Edge source '{edge.source}' not found in nodes")
            if edge.target not in valid_node_ids:
                raise ValueError(f"Edge target '{edge.target}' not found in nodes")

        # Check that entry points reference existing nodes
        for entry_point in self.entry_points:
            if entry_point not in valid_node_ids:
                raise ValueError(f"Entry point '{entry_point}' not found in nodes")

    def get_node_by_id(self, node_id: str) -> Optional[TopologyNode]:
        """Get a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_outgoing_edges(self, node_id: str) -> List[TopologyEdge]:
        """Get all edges that start from the given node."""
        return [edge for edge in self.edges if edge.source == node_id]

    def get_incoming_edges(self, node_id: str) -> List[TopologyEdge]:
        """Get all edges that end at the given node."""
        return [edge for edge in self.edges if edge.target == node_id]

    @property
    def max_depth(self) -> int:
        """Calculate the maximum depth of the graph."""
        if not self.nodes:
            return 0
        return max(node.position.depth for node in self.nodes)

    @property
    def branch_count(self) -> int:
        """Calculate the number of branches in the graph."""
        branch_count = 0
        for node in self.nodes:
            if node.is_router:
                # Count outgoing edges from router nodes
                outgoing_edges = self.get_outgoing_edges(node.id)
                if len(outgoing_edges) > 1:
                    branch_count += (
                        len(outgoing_edges) - 1
                    )  # Additional branches beyond linear flow
        return branch_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "nodes": [
                {
                    "id": node.id,
                    "module_type": node.module_type,
                    "name": node.name,
                    "platform": node.platform.value,
                    "position": {
                        "depth": node.position.depth,
                        "path": node.position.path,
                        "order": node.position.order,
                        "parent_id": node.position.parent_id,
                    },
                }
                for node in self.nodes
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "edge_type": edge.edge_type.value,
                    "metadata": edge.metadata,
                }
                for edge in self.edges
            ],
            "entry_points": self.entry_points.copy(),
            "platform": self.platform.value,
        }
