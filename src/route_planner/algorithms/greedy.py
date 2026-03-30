import heapq
import time

from route_planner.algorithms.common import (
    SearchResult,
    node_path_from_states,
    reconstruct_state_path,
    weighted_cost_from_node_path,
)
from route_planner.core.metrics import SearchMetrics
from route_planner.core.problem import RoutePlanningProblem


def run_greedy(problem, heuristic):
    # greedy best first - only uses heuristic, ignores actual path cost for ordering
    start_time = time.perf_counter()
    start_state = problem.initial_state()

    counter = 0
    frontier = [(heuristic(problem, start_state), counter, start_state)]
    parent = {}
    best_g = {start_state: 0.0}
    expanded = set()
    explored_nodes = []
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        if len(frontier) > max_frontier_size:
            max_frontier_size = len(frontier)

        _priority, _idx, state = heapq.heappop(frontier)
        if state in expanded:
            continue
        expanded.add(state)

        explored_nodes.append(state.current_node)
        nodes_expanded += 1

        if problem.is_goal(state):
            if state != start_state:
                state_path = reconstruct_state_path(parent, start_state, state)
            else:
                state_path = [start_state]
            node_path = node_path_from_states(state_path)
            runtime_ms = (time.perf_counter() - start_time) * 1000
            return SearchResult(
                algorithm="Greedy",
                solved=True,
                state_path=state_path,
                node_path=node_path,
                explored_nodes=explored_nodes,
                metrics=SearchMetrics(
                    weighted_path_cost=weighted_cost_from_node_path(problem.graph, node_path),
                    hops=max(0, len(node_path) - 1),
                    nodes_expanded=nodes_expanded,
                    runtime_ms=runtime_ms,
                    max_frontier_size=max_frontier_size,
                ),
                message="Solution found",
            )

        base_cost = best_g[state]
        for action, next_state in problem.successors(state, weighted=True):
            if next_state in expanded:
                continue
            next_cost = base_cost + action.edge_cost
            prev = best_g.get(next_state)
            if prev is not None and next_cost >= prev:
                continue
            best_g[next_state] = next_cost
            parent[next_state] = (state, action.edge_cost)
            counter += 1
            heapq.heappush(frontier, (heuristic(problem, next_state), counter, next_state))

    runtime_ms = (time.perf_counter() - start_time) * 1000
    return SearchResult(
        algorithm="Greedy",
        solved=False,
        explored_nodes=explored_nodes,
        metrics=SearchMetrics(
            weighted_path_cost=0.0,
            hops=0,
            nodes_expanded=nodes_expanded,
            runtime_ms=runtime_ms,
            max_frontier_size=max_frontier_size,
        ),
        message="No solution found",
    )
