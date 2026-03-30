from dataclasses import dataclass


# state = where we are + what we're carrying + what we've picked/delivered
@dataclass(frozen=True)
class SearchState:
    current_node: str
    carrying: tuple
    picked: tuple
    delivered: tuple

    def is_goal(self, total_requests):
        return len(self.delivered) == total_requests

    @staticmethod
    def canonical(current_node, carrying, picked, delivered):
        # sort so same state always has same hash
        return SearchState(
            current_node=current_node,
            carrying=tuple(sorted(carrying)),
            picked=tuple(sorted(picked)),
            delivered=tuple(sorted(delivered)),
        )
