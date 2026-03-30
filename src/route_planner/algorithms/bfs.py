from collections import deque
import time

from route_planner.algorithms.common import (
    SearchResult,
    node_path_from_states,
    reconstruct_state_path,
    weighted_cost_from_node_path,
)
from route_planner.core.metrics import SearchMetrics
from route_planner.core.problem import RoutePlanningProblem


def run_bfs(problem):
    start_time = time.perf_counter()
    start_state = problem.initial_state()

    # BFS uses a queue (FIFO), all edges treated as cost 1
    frontier = deque([start_state])
    visited = {start_state}
    parent = {}
    explored_nodes = []
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        if len(frontier) > max_frontier_size:
            max_frontier_size = len(frontier)

        state = frontier.popleft()
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
                algorithm="BFS",
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

        for _action, next_state in problem.successors(state, weighted=False):
            if next_state in visited:
                continue
            visited.add(next_state)
            parent[next_state] = (state, 1.0)
            frontier.append(next_state)

    runtime_ms = (time.perf_counter() - start_time) * 1000
    return SearchResult(
        algorithm="BFS",
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
