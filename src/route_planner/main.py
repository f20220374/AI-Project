from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from route_planner.io.loaders import load_graph, load_scenario, validate_scenario_against_graph
from route_planner.ui.app import RoutePlannerApp, format_metrics_table
from route_planner.ui.dashboard import VisualizerDashboard


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = PROJECT_ROOT / "data/campus_graph.json"
DEFAULT_SCENARIOS_DIR = PROJECT_ROOT / "scenarios"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Campus route-planning prototype")
    parser.add_argument("--scenario", default="easy.json", help="Scenario file inside scenarios/")
    parser.add_argument(
        "--mode",
        default="single",
        choices=["single", "compare", "ui"],
        help="single: one algorithm, compare: all algorithms, ui: launch UI shell",
    )
    parser.add_argument(
        "--algorithm",
        default="astar",
        choices=["bfs", "ucs", "greedy", "astar"],
        help="Algorithm for single mode",
    )
    parser.add_argument(
        "--heuristic",
        default="mst",
        choices=["nearest", "mst"],
        help="Heuristic for Greedy/A*",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Animate exploration and final route on campus map",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.02,
        help="Animation delay per expanded node in seconds",
    )
    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="List available scenarios and exit",
    )
    return parser.parse_args()


def available_scenarios(scenarios_dir: Path) -> list[str]:
    return sorted(path.name for path in scenarios_dir.glob("*.json"))


def print_result_details(result) -> None:
    print(f"\n[{result.algorithm}] solved={result.solved}")
    print(f"Path: {' -> '.join(result.node_path) if result.node_path else '(none)'}")
    print(f"weighted path cost: {result.metrics.weighted_path_cost:.1f}")
    print(f"hops: {result.metrics.hops}")
    print(f"nodes expanded: {result.metrics.nodes_expanded}")
    print(f"runtime (ms): {result.metrics.runtime_ms:.2f}")
    print(f"max frontier size: {result.metrics.max_frontier_size}")


def choose_from_prompt(options: Iterable[str], label: str) -> str:
    values = list(options)
    print(f"Select {label}:")
    for index, value in enumerate(values, start=1):
        print(f"  {index}. {value}")
    raw = input("Enter number: ").strip()
    selected_index = int(raw) - 1
    if selected_index < 0 or selected_index >= len(values):
        raise ValueError(f"Invalid {label} selection")
    return values[selected_index]


def main() -> None:
    args = parse_args()
    if args.list_scenarios:
        for name in available_scenarios(DEFAULT_SCENARIOS_DIR):
            print(name)
        return

    if args.mode == "ui":
        dashboard = VisualizerDashboard(graph_path=DEFAULT_GRAPH, scenarios_dir=DEFAULT_SCENARIOS_DIR)
        dashboard.run()
        return

    graph = load_graph(DEFAULT_GRAPH)
    scenario = load_scenario(DEFAULT_SCENARIOS_DIR / args.scenario)
    errors = validate_scenario_against_graph(scenario, graph)
    if errors:
        raise SystemExit("Scenario validation failed:\n- " + "\n- ".join(errors))

    app = RoutePlannerApp()
    app.config.animation_delay_seconds = args.delay

    print(f"Loaded graph: {len(graph.nodes_by_id)} nodes")
    print(f"Loaded scenario: {scenario.name} ({len(scenario.requests)} requests)")

    if args.mode in {"single", "ui"}:
        result = app.run_single(
            graph=graph,
            scenario=scenario,
            algorithm=args.algorithm,
            heuristic_name=args.heuristic,
            visualize=args.visualize,
        )
        print_result_details(result)
        return

    if args.mode == "compare":
        results = app.run_comparison(
            graph=graph,
            scenario=scenario,
            heuristic_name=args.heuristic,
            visualize=args.visualize,
        )
        print("\nComparison metrics")
        print(format_metrics_table(results))
        return


if __name__ == "__main__":
    main()
