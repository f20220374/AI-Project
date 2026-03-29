from __future__ import annotations

import heapq

from route_planner.core.problem import RoutePlanningProblem
from route_planner.models.state import SearchState


def nearest_remaining_distance(problem: RoutePlanningProblem, state: SearchState) -> float:
    """Admissible lower bound to nearest actionable remaining service node."""
    remaining_nodes = problem.actionable_service_nodes(state)
    if not remaining_nodes:
        return 0.0
    return min(problem.shortest_distance(state.current_node, node) for node in remaining_nodes)


def mst_plus_connectors(problem: RoutePlanningProblem, state: SearchState) -> float:
    """Admissible lower bound using connector from current node + MST of remaining nodes."""
    remaining_nodes = problem.mandatory_remaining_nodes(state)
    if not remaining_nodes:
        return 0.0

    nodes = sorted(remaining_nodes)
    connector = min(problem.shortest_distance(state.current_node, node) for node in nodes)
    if len(nodes) == 1:
        return connector

    mst_cost = _prim_mst_cost(problem, nodes)
    return connector + mst_cost


def _prim_mst_cost(problem: RoutePlanningProblem, nodes: list[str]) -> float:
    visited = {nodes[0]}
    heap: list[tuple[float, str]] = []
    for node in nodes[1:]:
        heapq.heappush(heap, (problem.shortest_distance(nodes[0], node), node))

    total = 0.0
    targets = set(nodes[1:])
    while targets:
        cost, to_node = heapq.heappop(heap)
        if to_node in visited:
            continue
        visited.add(to_node)
        targets.remove(to_node)
        total += cost
        for node in targets:
            heapq.heappush(heap, (problem.shortest_distance(to_node, node), node))
    return total
