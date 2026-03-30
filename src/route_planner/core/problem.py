from dataclasses import dataclass
import heapq

from route_planner.models.graph import CampusGraph
from route_planner.models.scenario import Scenario
from route_planner.models.state import SearchState


@dataclass(frozen=True)
class Action:
    to_node: str
    edge_cost: float


class RoutePlanningProblem:

    def __init__(self, graph, scenario):
        self.graph = graph
        self.scenario = scenario
        # map request id -> (pickup, drop)
        self.requests_by_id = {r.id: (r.pickup, r.drop) for r in scenario.requests}
        self._distance_cache = {}
        self._request_ids_sorted = tuple(sorted(self.requests_by_id.keys()))

    def initial_state(self):
        init = SearchState.canonical(
            current_node=self.scenario.start_node,
            carrying=(),
            picked=(),
            delivered=(),
        )
        return self.apply_auto_service(init)

    def is_goal(self, state):
        return state.is_goal(total_requests=len(self.scenario.requests))

    def successors(self, state, weighted=True):
        node_id = self.graph.node_id(state.current_node)
        for next_id, cost in self.graph.neighbors(node_id, weighted=weighted):
            next_key = self.graph.node_key(next_id)
            raw = SearchState.canonical(
                current_node=next_key,
                carrying=state.carrying,
                picked=state.picked,
                delivered=state.delivered,
            )
            served = self.apply_auto_service(raw)
            yield Action(to_node=next_key, edge_cost=cost), served

    def apply_auto_service(self, state):
        # drop deliveries first, then pick up new ones if capacity allows
        carrying = set(state.carrying)
        picked = set(state.picked)
        delivered = set(state.delivered)
        node = state.current_node

        to_drop = []
        for rid in sorted(carrying):
            _, drop = self.requests_by_id[rid]
            if drop == node:
                to_drop.append(rid)
        for rid in to_drop:
            carrying.remove(rid)
            delivered.add(rid)

        free = self.scenario.capacity - len(carrying)
        if free > 0:
            candidates = []
            for rid in self._request_ids_sorted:
                if rid in delivered or rid in picked:
                    continue
                pickup, _ = self.requests_by_id[rid]
                if pickup == node:
                    candidates.append(rid)
            for rid in candidates[:free]:
                carrying.add(rid)
                picked.add(rid)

        return SearchState.canonical(
            current_node=node,
            carrying=carrying,
            picked=picked,
            delivered=delivered,
        )

    def actionable_service_nodes(self, state):
        # nodes we still need to reach (drops for carried items, pickups for unstarted ones)
        carrying = set(state.carrying)
        picked = set(state.picked)
        delivered = set(state.delivered)
        nodes = set()
        for rid in self._request_ids_sorted:
            pickup, drop = self.requests_by_id[rid]
            if rid in delivered:
                continue
            if rid in carrying:
                nodes.add(drop)
            elif rid not in picked:
                nodes.add(pickup)
        return nodes

    def mandatory_remaining_nodes(self, state):
        # every node that must be visited before we're done
        carrying = set(state.carrying)
        picked = set(state.picked)
        delivered = set(state.delivered)
        nodes = set()
        for rid in self._request_ids_sorted:
            pickup, drop = self.requests_by_id[rid]
            if rid in delivered:
                continue
            if rid in carrying or rid in picked:
                nodes.add(drop)
            else:
                nodes.add(pickup)
                nodes.add(drop)
        return nodes

    def shortest_distance(self, from_key, to_key):
        from_id = self.graph.node_id(from_key)
        to_id = self.graph.node_id(to_key)
        if from_id == to_id:
            return 0.0
        if from_id not in self._distance_cache:
            self._distance_cache[from_id] = self._dijkstra_from(from_id)
        return self._distance_cache[from_id].get(to_id, float("inf"))

    def _dijkstra_from(self, source_id):
        dist = {source_id: 0.0}
        heap = [(0.0, source_id)]
        while heap:
            d, nid = heapq.heappop(heap)
            if d > dist[nid]:
                continue
            for nbr, cost in self.graph.neighbors(nid, weighted=True):
                nd = d + cost
                if nd < dist.get(nbr, float("inf")):
                    dist[nbr] = nd
                    heapq.heappush(heap, (nd, nbr))
        return dist
