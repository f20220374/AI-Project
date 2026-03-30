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


def run_astar(problem, heuristic):
    # f(n) = g(n) + h(n), expand lowest f first
    start_time = time.perf_counter()
    start_state = problem.initial_state()

    counter = 0
    h0 = heuristic(problem, start_state)
    frontier = [(h0, 0.0, counter, start_state)]
    best_g = {start_state: 0.0}
    parent = {}
    explored_nodes = []
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        if len(frontier) > max_frontier_size:
            max_frontier_size = len(frontier)

        _f, g_from_heap, _idx, state = heapq.heappop(frontier)

        # outdated entry - skip
        best_known = best_g.get(state)
        if best_known is None or g_from_heap > best_known:
            continue
        g_cost = best_known

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
                algorithm="A*",
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

        for action, next_state in problem.successors(state, weighted=True):
            new_g = g_cost + action.edge_cost
            if new_g >= best_g.get(next_state, float("inf")):
                continue
            best_g[next_state] = new_g
            parent[next_state] = (state, action.edge_cost)
            counter += 1
            f = new_g + heuristic(problem, next_state)
            heapq.heappush(frontier, (f, new_g, counter, next_state))

    runtime_ms = (time.perf_counter() - start_time) * 1000
    return SearchResult(
        algorithm="A*",
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
