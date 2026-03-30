from dataclasses import dataclass
from pathlib import Path

from route_planner.algorithms.astar import run_astar
from route_planner.algorithms.bfs import run_bfs
from route_planner.algorithms.common import SearchResult
from route_planner.algorithms.greedy import run_greedy
from route_planner.algorithms.ucs import run_ucs
from route_planner.core.problem import RoutePlanningProblem
from route_planner.heuristics import mst_plus_connectors, nearest_remaining_distance
from route_planner.models.graph import CampusGraph
from route_planner.models.scenario import Scenario
from route_planner.ui.renderer import MapRenderer


@dataclass
class UIConfig:
    title: str = "Campus Route Planner"
    map_image_path: Path = Path("assets/campus_map.png")
    animation_delay_seconds: float = 0.02


HEURISTICS = {
    "nearest": nearest_remaining_distance,
    "mst": mst_plus_connectors,
}


def run_algorithm(algorithm, problem, heuristic_name="mst"):
    if algorithm == "bfs":
        return run_bfs(problem)
    if algorithm == "ucs":
        return run_ucs(problem)
    if algorithm == "greedy":
        return run_greedy(problem, HEURISTICS[heuristic_name])
    if algorithm == "astar":
        return run_astar(problem, HEURISTICS[heuristic_name])
    raise ValueError(f"Unknown algorithm: {algorithm}")


def _scenario_node_sets(scenario):
    # pull out pickup and drop node lists from a scenario
    pickup_nodes = list({r.pickup for r in scenario.requests})
    drop_nodes = list({r.drop for r in scenario.requests})
    return pickup_nodes, drop_nodes


class RoutePlannerApp:

    def __init__(self, config=None):
        self.config = config or UIConfig()
        self.renderer = MapRenderer(self.config.map_image_path)

    def run_single(self, graph, scenario, algorithm, heuristic_name, visualize):
        problem = RoutePlanningProblem(graph, scenario)
        result = run_algorithm(algorithm=algorithm, problem=problem, heuristic_name=heuristic_name)
        if visualize:
            pickup_nodes, drop_nodes = _scenario_node_sets(scenario)
            self.renderer.animate_exploration(
                graph=graph,
                result=result,
                delay_seconds=self.config.animation_delay_seconds,
                show=True,
                start_node=scenario.start_node,
                pickup_nodes=pickup_nodes,
                drop_nodes=drop_nodes,
            )
        return result

    def run_comparison(self, graph, scenario, heuristic_name, visualize):
        results = []
        for algo in ("bfs", "ucs", "greedy", "astar"):
            result = self.run_single(
                graph=graph,
                scenario=scenario,
                algorithm=algo,
                heuristic_name=heuristic_name,
                visualize=False,  # don't animate individual runs in compare mode
            )
            results.append(result)
        if visualize:
            pickup_nodes, drop_nodes = _scenario_node_sets(scenario)
            self.renderer.draw_compare(
                graph=graph,
                results=results,
                show=True,
                start_node=scenario.start_node,
                pickup_nodes=pickup_nodes,
                drop_nodes=drop_nodes,
            )
        return results


def format_metrics_table(results):
    headers = ["Algorithm", "Solved", "Cost", "Hops", "Expanded", "Runtime(ms)", "MaxFrontier"]
    rows = []
    for r in results:
        rows.append([
            r.algorithm,
            "yes" if r.solved else "no",
            f"{r.metrics.weighted_path_cost:.1f}",
            str(r.metrics.hops),
            str(r.metrics.nodes_expanded),
            f"{r.metrics.runtime_ms:.2f}",
            str(r.metrics.max_frontier_size),
        ])

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(val))

    def make_line(vals):
        return " | ".join(vals[i].ljust(col_widths[i]) for i in range(len(vals)))

    divider = "-+-".join("-" * w for w in col_widths)
    lines = [make_line(headers), divider]
    for row in rows:
        lines.append(make_line(row))
    return "\n".join(lines)
