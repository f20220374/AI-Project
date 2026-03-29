from __future__ import annotations

from dataclasses import dataclass
import heapq
from typing import Dict, Iterable, List, Set, Tuple

from route_planner.models.graph import CampusGraph
from route_planner.models.scenario import Scenario
from route_planner.models.state import SearchState


@dataclass(frozen=True)
class Action:
    to_node: str
    edge_cost: float


class RoutePlanningProblem:
    """Pickup-delivery route-planning problem over a fixed campus graph."""

    def __init__(self, graph: CampusGraph, scenario: Scenario) -> None:
        self.graph = graph
        self.scenario = scenario
        self.requests_by_id: Dict[str, Tuple[str, str]] = {
            request.id: (request.pickup, request.drop) for request in scenario.requests
        }
        self._distance_cache: Dict[int, Dict[int, float]] = {}
        self._request_ids_sorted = tuple(sorted(self.requests_by_id.keys()))

    def initial_state(self) -> SearchState:
        initial = SearchState.canonical(
            current_node=self.scenario.start_node,
            carrying=(),
            picked=(),
            delivered=(),
        )
        return self.apply_auto_service(initial)

    def is_goal(self, state: SearchState) -> bool:
        return state.is_goal(total_requests=len(self.scenario.requests))

    def successors(self, state: SearchState, weighted: bool) -> Iterable[Tuple[Action, SearchState]]:
        current_node_id = self.graph.node_id(state.current_node)
        for next_node_id, search_cost in self.graph.neighbors(current_node_id, weighted=weighted):
            next_node_key = self.graph.node_key(next_node_id)
            raw_next_state = SearchState.canonical(
                current_node=next_node_key,
                carrying=state.carrying,
                picked=state.picked,
                delivered=state.delivered,
            )
            served_next_state = self.apply_auto_service(raw_next_state)
            yield Action(to_node=next_node_key, edge_cost=search_cost), served_next_state

    def apply_auto_service(self, state: SearchState) -> SearchState:
        """Apply deterministic drop-then-pickup semantics at state's current node."""
        carrying: Set[str] = set(state.carrying)
        picked: Set[str] = set(state.picked)
        delivered: Set[str] = set(state.delivered)
        current_node = state.current_node

        to_drop: List[str] = []
        for request_id in sorted(carrying):
            _pickup_node, drop_node = self.requests_by_id[request_id]
            if drop_node == current_node:
                to_drop.append(request_id)
        for request_id in to_drop:
            carrying.remove(request_id)
            delivered.add(request_id)

        free_slots = self.scenario.capacity - len(carrying)
        if free_slots > 0:
            pick_candidates: List[str] = []
            for request_id in self._request_ids_sorted:
                if request_id in delivered or request_id in picked:
                    continue
                pickup_node, _drop_node = self.requests_by_id[request_id]
                if pickup_node == current_node:
                    pick_candidates.append(request_id)
            for request_id in pick_candidates[:free_slots]:
                carrying.add(request_id)
                picked.add(request_id)

        return SearchState.canonical(
            current_node=current_node,
            carrying=carrying,
            picked=picked,
            delivered=delivered,
        )

    def actionable_service_nodes(self, state: SearchState) -> Set[str]:
        """Service nodes that can be valid immediate next work targets from this state."""
        carrying = set(state.carrying)
        picked = set(state.picked)
        delivered = set(state.delivered)
        nodes: Set[str] = set()
        for request_id in self._request_ids_sorted:
            pickup, drop = self.requests_by_id[request_id]
            if request_id in delivered:
                continue
            if request_id in carrying:
                nodes.add(drop)
            elif request_id not in picked:
                nodes.add(pickup)
        return nodes

    def mandatory_remaining_nodes(self, state: SearchState) -> Set[str]:
        """All nodes that must still be visited to complete remaining requests."""
        carrying = set(state.carrying)
        picked = set(state.picked)
        delivered = set(state.delivered)
        nodes: Set[str] = set()
        for request_id in self._request_ids_sorted:
            pickup, drop = self.requests_by_id[request_id]
            if request_id in delivered:
                continue
            if request_id in carrying:
                nodes.add(drop)
            elif request_id in picked:
                nodes.add(drop)
            else:
                nodes.add(pickup)
                nodes.add(drop)
        return nodes

    def shortest_distance(self, from_key: str, to_key: str) -> float:
        """Weighted shortest-path distance between two graph node keys."""
        from_id = self.graph.node_id(from_key)
        to_id = self.graph.node_id(to_key)
        if from_id == to_id:
            return 0.0
        if from_id not in self._distance_cache:
            self._distance_cache[from_id] = self._dijkstra_from(from_id)
        return self._distance_cache[from_id][to_id]

    def _dijkstra_from(self, source_id: int) -> Dict[int, float]:
        distances: Dict[int, float] = {source_id: 0.0}
        heap: List[Tuple[float, int]] = [(0.0, source_id)]
        while heap:
            current_distance, node_id = heapq.heappop(heap)
            if current_distance > distances[node_id]:
                continue
            for neighbor_id, edge_cost in self.graph.neighbors(node_id, weighted=True):
                next_distance = current_distance + edge_cost
                prev_distance = distances.get(neighbor_id)
                if prev_distance is None or next_distance < prev_distance:
                    distances[neighbor_id] = next_distance
                    heapq.heappush(heap, (next_distance, neighbor_id))
        return distances
