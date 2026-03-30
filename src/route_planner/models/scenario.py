from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    id: str
    pickup: str
    drop: str


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    start_node: str
    capacity: int
    requests: list

    def request_ids(self):
        return tuple(r.id for r in sorted(self.requests, key=lambda r: r.id))
