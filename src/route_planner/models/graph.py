from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    id: int
    key: str
    label: str
    x: float
    y: float
    type: str


@dataclass(frozen=True)
class Edge:
    from_id: int
    to_id: int
    cost: float


@dataclass
class CampusGraph:
    nodes_by_id: dict
    node_id_by_key: dict
    adjacency: dict
    edge_costs: dict

    def neighbors(self, node_id, weighted=True):
        for nxt, cost in self.adjacency.get(node_id, []):
            yield (nxt, cost if weighted else 1.0)

    def node_key(self, node_id):
        return self.nodes_by_id[node_id].key

    def node_id(self, node_key):
        return self.node_id_by_key[node_key]

    def edge_cost(self, from_id, to_id):
        return self.edge_costs[(from_id, to_id)]

    def weighted_path_cost(self, node_path):
        if len(node_path) < 2:
            return 0.0
        total = 0.0
        for i in range(len(node_path) - 1):
            a = self.node_id(node_path[i])
            b = self.node_id(node_path[i + 1])
            total += self.edge_cost(a, b)
        return total
