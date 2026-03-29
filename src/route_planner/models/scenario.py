from __future__ import annotations

from dataclasses import dataclass
from typing import List


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
    requests: List[Request]

    def request_ids(self) -> tuple[str, ...]:
        return tuple(request.id for request in sorted(self.requests, key=lambda value: value.id))
