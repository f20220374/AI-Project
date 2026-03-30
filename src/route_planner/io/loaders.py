import json
from pathlib import Path

from route_planner.models.graph import CampusGraph, Node
from route_planner.models.scenario import Request, Scenario


def load_graph(path):
    data = json.loads(path.read_text())
    nodes = {}
    for n in data["nodes"]:
        nodes[n["id"]] = Node(
            id=n["id"],
            key=n["key"],
            label=n.get("label", n["key"]),
            x=n["x"],
            y=n["y"],
            type=n.get("type", "L"),
        )

    if len(nodes) != len(data["nodes"]):
        raise ValueError("Duplicate node IDs in graph file.")

    node_id_by_key = {n.key: n.id for n in nodes.values()}
    if len(node_id_by_key) != len(nodes):
        raise ValueError("Duplicate node keys in graph file.")

    adjacency = {nid: [] for nid in nodes}
    edge_costs = {}
    for e in data["edges"]:
        a, b, c = e["from"], e["to"], float(e["cost"])
        if a not in nodes or b not in nodes:
            raise ValueError(f"Edge references unknown node: {a}->{b}")
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


def load_scenario(path):
    data = json.loads(path.read_text())
    requests = [Request(id=r["id"], pickup=r["pickup"], drop=r["drop"]) for r in data["requests"]]
    if len({r.id for r in requests}) != len(requests):
        raise ValueError(f"Duplicate request IDs in: {path.name}")
    return Scenario(
        name=data["name"],
        description=data.get("description", ""),
        start_node=data["start_node"],
        capacity=int(data.get("capacity", 2)),
        requests=requests,
    )


def validate_scenario_against_graph(scenario, graph):
    errors = []
    if scenario.capacity <= 0:
        errors.append("capacity must be positive")
    if scenario.start_node not in graph.node_id_by_key:
        errors.append(f"unknown start_node: {scenario.start_node}")
    for r in scenario.requests:
        if r.pickup not in graph.node_id_by_key:
            errors.append(f"request {r.id} pickup unknown: {r.pickup}")
        if r.drop not in graph.node_id_by_key:
            errors.append(f"request {r.id} drop unknown: {r.drop}")
    return errors
