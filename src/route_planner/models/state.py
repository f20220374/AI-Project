from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class SearchState:
    current_node: str
    carrying: Tuple[str, ...]
    picked: Tuple[str, ...]
    delivered: Tuple[str, ...]

    def is_goal(self, total_requests: int) -> bool:
        return len(self.delivered) == total_requests

    @staticmethod
    def canonical(
        current_node: str,
        carrying: Iterable[str],
        picked: Iterable[str],
        delivered: Iterable[str],
    ) -> "SearchState":
        return SearchState(
            current_node=current_node,
            carrying=tuple(sorted(carrying)),
            picked=tuple(sorted(picked)),
            delivered=tuple(sorted(delivered)),
        )
