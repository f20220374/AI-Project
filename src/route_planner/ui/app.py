from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable

from route_planner.algorithms.astar import run_astar
from route_planner.algorithms.bfs import run_bfs
from route_planner.algorithms.common import SearchResult
from route_planner.algorithms.greedy import run_greedy
from route_planner.algorithms.ucs import run_ucs
from route_planner.core.problem import RoutePlanningProblem
from route_planner.heuristics import mst_plus_connectors, nearest_remaining_distance
from route_planner.models.graph import CampusGraph
from route_planner.models.scenario import Scenario
from route_planner.models.state import SearchState
from route_planner.ui.renderer import MapRenderer

@dataclass
class UIConfig:
    title: str = "Campus Route Planner"
    map_image_path: Path = Path("assets/campus_map.png")
    animation_delay_seconds: float = 0.02


HEURISTICS: Dict[str, Callable[[RoutePlanningProblem, SearchState], float]] = {
    "nearest": nearest_remaining_distance,
    "mst": mst_plus_connectors,
}


def run_algorithm(
    algorithm: str,
    problem: RoutePlanningProblem,
    heuristic_name: str = "mst",
) -> SearchResult:
    if algorithm == "bfs":
        return run_bfs(problem)
    if algorithm == "ucs":
        return run_ucs(problem)
    if algorithm == "greedy":
        return run_greedy(problem, HEURISTICS[heuristic_name])
    if algorithm == "astar":
        return run_astar(problem, HEURISTICS[heuristic_name])
    raise ValueError(f"Unsupported algorithm: {algorithm}")


class RoutePlannerApp:
    """Application orchestrator for search execution and visualization."""

    def __init__(self, config: UIConfig | None = None) -> None:
        self.config = config or UIConfig()
        self.renderer = MapRenderer(self.config.map_image_path)

    def run_single(
        self,
        graph: CampusGraph,
        scenario: Scenario,
        algorithm: str,
        heuristic_name: str,
        visualize: bool,
    ) -> SearchResult:
        problem = RoutePlanningProblem(graph, scenario)
        result = run_algorithm(algorithm=algorithm, problem=problem, heuristic_name=heuristic_name)
        if visualize:
            self.renderer.animate_exploration(
                graph=graph,
                result=result,
                delay_seconds=self.config.animation_delay_seconds,
                show=True,
            )
        return result

    def run_comparison(
        self,
        graph: CampusGraph,
        scenario: Scenario,
        heuristic_name: str,
        visualize: bool,
    ) -> list[SearchResult]:
        results: list[SearchResult] = []
        for algorithm in ("bfs", "ucs", "greedy", "astar"):
            result = self.run_single(
                graph=graph,
                scenario=scenario,
                algorithm=algorithm,
                heuristic_name=heuristic_name,
                visualize=visualize,
            )
            results.append(result)
        return results

    def run(self) -> None:
        print("Use route_planner.main entrypoint to run scenario + algorithm selection.")


def format_metrics_table(results: Iterable[SearchResult]) -> str:
    headers = ["Algorithm", "Solved", "Cost", "Hops", "Expanded", "Runtime(ms)", "MaxFrontier"]
    rows = []
    for result in results:
        rows.append(
            [
                result.algorithm,
                "yes" if result.solved else "no",
                f"{result.metrics.weighted_path_cost:.1f}",
                str(result.metrics.hops),
                str(result.metrics.nodes_expanded),
                f"{result.metrics.runtime_ms:.2f}",
                str(result.metrics.max_frontier_size),
            ]
        )

    col_widths = [len(h) for h in headers]
    for row in rows:
        for index, value in enumerate(row):
            col_widths[index] = max(col_widths[index], len(value))

    def _line(values: list[str]) -> str:
        return " | ".join(values[index].ljust(col_widths[index]) for index in range(len(values)))

    divider = "-+-".join("-" * width for width in col_widths)
    output = [_line(headers), divider]
    for row in rows:
        output.append(_line(row))
    return "\n".join(output)
