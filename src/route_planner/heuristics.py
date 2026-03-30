import heapq


def nearest_remaining_distance(problem, state):
    # h1: distance to nearest unvisited service node
    remaining = problem.actionable_service_nodes(state)
    if not remaining:
        return 0.0
    return min(problem.shortest_distance(state.current_node, n) for n in remaining)


def mst_plus_connectors(problem, state):
    # h2: connector from current node + MST over all remaining nodes
    # stronger than h1 because it considers all remaining stops together
    remaining = problem.mandatory_remaining_nodes(state)
    if not remaining:
        return 0.0

    nodes = sorted(remaining)
    connector = min(problem.shortest_distance(state.current_node, n) for n in nodes)
    if len(nodes) == 1:
        return connector

    return connector + _prim_mst(problem, nodes)


def _prim_mst(problem, nodes):
    # Prim's MST on remaining nodes using precomputed shortest distances
    visited = {nodes[0]}
    heap = []
    for n in nodes[1:]:
        heapq.heappush(heap, (problem.shortest_distance(nodes[0], n), n))

    total = 0.0
    remaining = set(nodes[1:])
    while remaining:
        cost, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        remaining.remove(node)
        total += cost
        for other in remaining:
            heapq.heappush(heap, (problem.shortest_distance(node, other), other))
    return total
