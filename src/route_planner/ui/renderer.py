from __future__ import annotations

from pathlib import Path
from typing import Sequence

from route_planner.algorithms.common import SearchResult
from route_planner.core.metrics import SearchMetrics
from route_planner.models.graph import CampusGraph


try:
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - runtime environment dependent
    mpimg = None
    plt = None


class MapRenderer:
    """Visualization adapter for campus map + graph overlays.

    `assets/campus_map.png` is treated as background visualization only.
    """

    def __init__(self, map_image_path: Path) -> None:
        self.map_image_path = map_image_path

    def draw_static(self, graph: CampusGraph, title: str = "Campus Graph", show: bool = True) -> None:
        fig, ax = self._build_base_figure(graph, title)
        if show:
            plt.show()
        else:
            plt.close(fig)

    def animate_exploration(
        self,
        graph: CampusGraph,
        result: SearchResult,
        delay_seconds: float = 0.02,
        show: bool = True,
    ) -> None:
        title = f"{result.algorithm}: Search Exploration"
        fig, ax = self._build_base_figure(graph, title)
        metrics_text = self._format_metrics(result.metrics)

        explored_ids = [graph.node_id(node) for node in result.explored_nodes if node in graph.node_id_by_key]
        route_ids = [graph.node_id(node) for node in result.node_path if node in graph.node_id_by_key]

        visited_scatter = ax.scatter([], [], c="#f59e0b", s=24, label="Explored")
        route_line, = ax.plot([], [], color="#ef4444", linewidth=3, label="Final Route")

        ax.text(
            0.01,
            0.99,
            metrics_text,
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=9,
            bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "#d1d5db"},
        )

        visited_xy: list[tuple[float, float]] = []
        for node_id in explored_ids:
            node = graph.nodes_by_id[node_id]
            visited_xy.append((node.x, node.y))
            visited_scatter.set_offsets(visited_xy)
            plt.pause(delay_seconds)

        if len(route_ids) >= 2:
            xs = [graph.nodes_by_id[node_id].x for node_id in route_ids]
            ys = [graph.nodes_by_id[node_id].y for node_id in route_ids]
            route_line.set_data(xs, ys)

        ax.legend(loc="lower right")
        if show:
            plt.show()
        else:
            plt.close(fig)

    def draw_final_route(self, graph: CampusGraph, node_path: Sequence[str], show: bool = True) -> None:
        fig, ax = self._build_base_figure(graph, "Final Route")
        route_ids = [graph.node_id(node) for node in node_path]
        if len(route_ids) >= 2:
            xs = [graph.nodes_by_id[node_id].x for node_id in route_ids]
            ys = [graph.nodes_by_id[node_id].y for node_id in route_ids]
            ax.plot(xs, ys, color="#ef4444", linewidth=3, label="Route")
            ax.legend(loc="lower right")
        if show:
            plt.show()
        else:
            plt.close(fig)

    def _build_base_figure(self, graph: CampusGraph, title: str):
        if plt is None:
            raise RuntimeError("matplotlib is required for visualization. Install with: pip install matplotlib")

        fig, ax = plt.subplots(figsize=(10, 8))
        width, height = self._draw_background(ax, graph)

        for from_id, neighbors in graph.adjacency.items():
            from_node = graph.nodes_by_id[from_id]
            for to_id, _cost in neighbors:
                if to_id < from_id:
                    continue
                to_node = graph.nodes_by_id[to_id]
                ax.plot([from_node.x, to_node.x], [from_node.y, to_node.y], color="#9ca3af", linewidth=1.0, alpha=0.7)

        xs = [node.x for node in graph.nodes_by_id.values()]
        ys = [node.y for node in graph.nodes_by_id.values()]
        colors = ["#2563eb" if node.type == "L" else "#14b8a6" for node in graph.nodes_by_id.values()]
        ax.scatter(xs, ys, c=colors, s=30, edgecolors="white", linewidths=0.5, label="Nodes")

        for node in graph.nodes_by_id.values():
            ax.text(node.x + 6, node.y - 6, node.key, fontsize=6, color="#111827")

        ax.set_title(title)
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        return fig, ax

    def _draw_background(self, ax, graph: CampusGraph) -> tuple[float, float]:
        if mpimg is not None and self.map_image_path.exists():
            try:
                image = mpimg.imread(self.map_image_path)
                height, width = image.shape[0], image.shape[1]
                ax.imshow(image, extent=[0, width, height, 0])
                return float(width), float(height)
            except Exception:
                pass

        max_x = max(node.x for node in graph.nodes_by_id.values()) + 80
        max_y = max(node.y for node in graph.nodes_by_id.values()) + 80
        return max_x, max_y

    @staticmethod
    def _format_metrics(metrics: SearchMetrics) -> str:
        return (
            f"weighted cost: {metrics.weighted_path_cost:.1f}\n"
            f"hops: {metrics.hops}\n"
            f"expanded: {metrics.nodes_expanded}\n"
            f"runtime (ms): {metrics.runtime_ms:.2f}\n"
            f"max frontier: {metrics.max_frontier_size}"
        )
