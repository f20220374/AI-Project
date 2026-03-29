from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from route_planner.core.metrics import SearchMetrics
from route_planner.models.graph import CampusGraph
from route_planner.models.state import SearchState


@dataclass
class SearchResult:
    algorithm: str
    solved: bool
    state_path: List[SearchState] = field(default_factory=list)
    node_path: List[str] = field(default_factory=list)
    explored_nodes: List[str] = field(default_factory=list)
    metrics: SearchMetrics = field(default_factory=SearchMetrics)
    message: str = ""


ParentMap = Dict[SearchState, Tuple[SearchState, float]]


def reconstruct_state_path(
    parent: ParentMap,
    start_state: SearchState,
    goal_state: SearchState,
) -> List[SearchState]:
    path: List[SearchState] = [goal_state]
    cursor = goal_state
    while cursor != start_state:
        cursor = parent[cursor][0]
        path.append(cursor)
    path.reverse()
    return path


def node_path_from_states(state_path: List[SearchState]) -> List[str]:
    return [state.current_node for state in state_path]


def weighted_cost_from_node_path(graph: CampusGraph, node_path: List[str]) -> float:
    return graph.weighted_path_cost(node_path)
