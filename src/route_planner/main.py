import argparse
from pathlib import Path

from route_planner.io.loaders import load_graph, load_scenario, validate_scenario_against_graph
from route_planner.ui.app import RoutePlannerApp, format_metrics_table
from route_planner.ui.dashboard import VisualizerDashboard


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = PROJECT_ROOT / "data/campus_graph.json"
DEFAULT_SCENARIOS_DIR = PROJECT_ROOT / "scenarios"


def parse_args():
    parser = argparse.ArgumentParser(description="Campus route planner")
    parser.add_argument("--scenario", default="easy.json", help="scenario file to use")
    parser.add_argument("--mode", default="single", choices=["single", "compare", "ui"])
    parser.add_argument("--algorithm", default="astar", choices=["bfs", "ucs", "greedy", "astar"])
    parser.add_argument("--heuristic", default="mst", choices=["nearest", "mst"])
    parser.add_argument("--visualize", action="store_true", help="show map animation")
    parser.add_argument("--delay", type=float, default=0.02, help="animation delay in seconds")
    parser.add_argument("--list-scenarios", action="store_true")
    return parser.parse_args()


def print_result(result):
    print(f"\n[{result.algorithm}] solved={result.solved}")
    print(f"path: {' -> '.join(result.node_path) if result.node_path else '(none)'}")
    print(f"cost: {result.metrics.weighted_path_cost:.1f}")
    print(f"hops: {result.metrics.hops}")
    print(f"expanded: {result.metrics.nodes_expanded}")
    print(f"time: {result.metrics.runtime_ms:.2f}ms")
    print(f"max frontier: {result.metrics.max_frontier_size}")


def main():
    args = parse_args()

    if args.list_scenarios:
        for f in sorted(p.name for p in DEFAULT_SCENARIOS_DIR.glob("*.json")):
            print(f)
        return

    if args.mode == "ui":
        dashboard = VisualizerDashboard(graph_path=DEFAULT_GRAPH, scenarios_dir=DEFAULT_SCENARIOS_DIR)
        dashboard.run()
        return

    graph = load_graph(DEFAULT_GRAPH)
    scenario = load_scenario(DEFAULT_SCENARIOS_DIR / args.scenario)
    errors = validate_scenario_against_graph(scenario, graph)
    if errors:
        raise SystemExit("Validation errors:\n- " + "\n- ".join(errors))

    app = RoutePlannerApp()
    app.config.animation_delay_seconds = args.delay

    print(f"graph: {len(graph.nodes_by_id)} nodes")
    print(f"scenario: {scenario.name} ({len(scenario.requests)} requests)")

    if args.mode == "single":
        result = app.run_single(
            graph=graph,
            scenario=scenario,
            algorithm=args.algorithm,
            heuristic_name=args.heuristic,
            visualize=args.visualize,
        )
        print_result(result)

    elif args.mode == "compare":
        results = app.run_comparison(
            graph=graph,
            scenario=scenario,
            heuristic_name=args.heuristic,
            visualize=args.visualize,
        )
        print("\nComparison:")
        print(format_metrics_table(results))


if __name__ == "__main__":
    main()
