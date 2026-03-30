from dataclasses import dataclass, field

from route_planner.core.metrics import SearchMetrics
from route_planner.models.graph import CampusGraph
from route_planner.models.state import SearchState


@dataclass
class SearchResult:
    algorithm: str
    solved: bool
    state_path: list = field(default_factory=list)
    node_path: list = field(default_factory=list)
    explored_nodes: list = field(default_factory=list)
    metrics: SearchMetrics = field(default_factory=SearchMetrics)
    message: str = ""


def reconstruct_state_path(parent, start_state, goal_state):
    # walk back through parent map to rebuild the path
    path = [goal_state]
    cur = goal_state
    while cur != start_state:
        cur = parent[cur][0]
        path.append(cur)
    path.reverse()
    return path


def node_path_from_states(state_path):
    return [s.current_node for s in state_path]


def weighted_cost_from_node_path(graph, node_path):
    return graph.weighted_path_cost(node_path)
