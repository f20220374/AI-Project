from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from route_planner.models.graph import CampusGraph, Node
from route_planner.models.scenario import Request, Scenario


def load_graph(path: Path) -> CampusGraph:
    payload = json.loads(path.read_text())
    nodes = {
        node["id"]: Node(
            id=node["id"],
            key=node["key"],
            label=node.get("label", node["key"]),
            x=node["x"],
            y=node["y"],
            type=node.get("type", "L"),
        )
        for node in payload["nodes"]
    }
    if len(nodes) != len(payload["nodes"]):
        raise ValueError("Duplicate node IDs found in graph file.")

    node_id_by_key = {node.key: node.id for node in nodes.values()}
    if len(node_id_by_key) != len(nodes):
        raise ValueError("Duplicate node keys found in graph file.")

    adjacency: Dict[int, List[tuple[int, float]]] = {node_id: [] for node_id in nodes}
    edge_costs: Dict[tuple[int, int], float] = {}
    for edge in payload["edges"]:
        a = edge["from"]
        b = edge["to"]
        c = float(edge["cost"])
        if a not in nodes or b not in nodes:
            raise ValueError(f"Edge references missing node: {a}->{b}")
        adjacency[a].append((b, c))
        adjacency[b].append((a, c))
        edge_costs[(a, b)] = c
        edge_costs[(b, a)] = c
    return CampusGraph(
        nodes_by_id=nodes,
        node_id_by_key=node_id_by_key,
        adjacency=adjacency,
        edge_costs=edge_costs,
    )


def load_scenario(path: Path) -> Scenario:
    payload = json.loads(path.read_text())
    requests = [
        Request(id=request["id"], pickup=request["pickup"], drop=request["drop"])
        for request in payload["requests"]
    ]
    if len({request.id for request in requests}) != len(requests):
        raise ValueError(f"Duplicate request IDs in scenario: {path.name}")
    return Scenario(
        name=payload["name"],
        description=payload.get("description", ""),
        start_node=payload["start_node"],
        capacity=int(payload.get("capacity", 2)),
        requests=requests,
    )


def validate_scenario_against_graph(scenario: Scenario, graph: CampusGraph) -> list[str]:
    errors: list[str] = []
    if scenario.capacity <= 0:
        errors.append("Scenario capacity must be positive")
    if scenario.start_node not in graph.node_id_by_key:
        errors.append(f"Unknown start_node: {scenario.start_node}")
    for request in scenario.requests:
        if request.pickup not in graph.node_id_by_key:
            errors.append(f"Request {request.id} pickup unknown: {request.pickup}")
        if request.drop not in graph.node_id_by_key:
            errors.append(f"Request {request.id} drop unknown: {request.drop}")
    return errors
