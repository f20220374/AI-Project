from dataclasses import dataclass


@dataclass
class SearchMetrics:
    weighted_path_cost: float = 0.0
    hops: int = 0
    nodes_expanded: int = 0
    runtime_ms: float = 0.0
    max_frontier_size: int = 0
