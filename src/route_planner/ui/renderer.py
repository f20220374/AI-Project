from pathlib import Path

try:
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt
except Exception:
    mpimg = None
    plt = None


class MapRenderer:

    def __init__(self, map_image_path):
        self.map_image_path = map_image_path

    def animate_exploration(self, graph, result, delay_seconds=0.02, show=True,
                            start_node=None, pickup_nodes=None, drop_nodes=None):
        if plt is None:
            raise RuntimeError("matplotlib not installed. Run: pip install matplotlib")

        pickup_nodes = pickup_nodes or []
        drop_nodes = drop_nodes or []

        fig, ax = plt.subplots(figsize=(10, 8))
        width, height = self._draw_background(ax, graph)
        self._draw_edges(ax, graph)
        self._draw_base_nodes(ax, graph)

        # mark pickup/drop/start nodes
        self._mark_nodes(ax, graph, pickup_nodes, color="blue", size=80, label="Pickup", marker="^")
        self._mark_nodes(ax, graph, drop_nodes, color="red", size=80, label="Drop", marker="v")
        if start_node and start_node in graph.node_id_by_key:
            nid = graph.node_id(start_node)
            n = graph.nodes_by_id[nid]
            ax.scatter([n.x], [n.y], c="green", s=120, zorder=8, label="Start", marker="*")

        # explored = grey, final path = yellow
        explored_ids = [graph.node_id(n) for n in result.explored_nodes if n in graph.node_id_by_key]
        grey_scatter = ax.scatter([], [], c="grey", s=22, alpha=0.7, zorder=4, label="Explored")
        route_line, = ax.plot([], [], color="yellow", linewidth=3, zorder=6, label="Path")

        metrics_str = (
            f"cost: {result.metrics.weighted_path_cost:.0f}  "
            f"hops: {result.metrics.hops}  "
            f"expanded: {result.metrics.nodes_expanded}  "
            f"time: {result.metrics.runtime_ms:.1f}ms"
        )
        ax.set_title(f"{result.algorithm}   {metrics_str}", fontsize=10)

        visited_xy = []
        for nid in explored_ids:
            n = graph.nodes_by_id[nid]
            visited_xy.append((n.x, n.y))
            grey_scatter.set_offsets(visited_xy)
            plt.pause(delay_seconds)

        # show final route
        route_ids = [graph.node_id(n) for n in result.node_path if n in graph.node_id_by_key]
        if len(route_ids) >= 2:
            xs = [graph.nodes_by_id[i].x for i in route_ids]
            ys = [graph.nodes_by_id[i].y for i in route_ids]
            route_line.set_data(xs, ys)

        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.legend(loc="lower right", fontsize=8)
        if show:
            plt.show()
        else:
            plt.close(fig)

    def draw_compare(self, graph, results, show=True,
                     start_node=None, pickup_nodes=None, drop_nodes=None):
        # show all algorithms side by side
        if plt is None:
            raise RuntimeError("matplotlib not installed.")

        pickup_nodes = pickup_nodes or []
        drop_nodes = drop_nodes or []
        total = len(results)
        cols = 2
        rows = (total + 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(14, 6 * rows))
        if total == 1:
            axes = [[axes]]
        elif rows == 1:
            axes = [list(axes)]

        for idx, result in enumerate(results):
            r, c = divmod(idx, cols)
            ax = axes[r][c]
            width, height = self._draw_background(ax, graph)
            self._draw_edges(ax, graph)
            self._draw_base_nodes(ax, graph)

            # grey for explored
            explored_ids = [graph.node_id(n) for n in result.explored_nodes if n in graph.node_id_by_key]
            if explored_ids:
                ex = [graph.nodes_by_id[i].x for i in explored_ids]
                ey = [graph.nodes_by_id[i].y for i in explored_ids]
                ax.scatter(ex, ey, c="grey", s=16, alpha=0.6, zorder=4)

            # yellow for path
            route_ids = [graph.node_id(n) for n in result.node_path if n in graph.node_id_by_key]
            if len(route_ids) >= 2:
                xs = [graph.nodes_by_id[i].x for i in route_ids]
                ys = [graph.nodes_by_id[i].y for i in route_ids]
                ax.plot(xs, ys, color="yellow", linewidth=2.5, zorder=6)

            self._mark_nodes(ax, graph, pickup_nodes, color="blue", size=60, label="Pickup", marker="^")
            self._mark_nodes(ax, graph, drop_nodes, color="red", size=60, label="Drop", marker="v")
            if start_node and start_node in graph.node_id_by_key:
                nid = graph.node_id(start_node)
                n_obj = graph.nodes_by_id[nid]
                ax.scatter([n_obj.x], [n_obj.y], c="green", s=100, zorder=8, marker="*")

            metrics_str = (
                f"cost={result.metrics.weighted_path_cost:.0f}  "
                f"exp={result.metrics.nodes_expanded}  "
                f"{result.metrics.runtime_ms:.1f}ms"
            )
            solved = "ok" if result.solved else "FAIL"
            ax.set_title(f"{result.algorithm} ({solved})\n{metrics_str}", fontsize=9)
            ax.set_xlim(0, width)
            ax.set_ylim(height, 0)
            ax.set_xticks([])
            ax.set_yticks([])

        # hide empty subplots if odd number of algorithms
        for idx in range(total, rows * cols):
            r, c = divmod(idx, cols)
            axes[r][c].set_visible(False)

        fig.suptitle("Algorithm Comparison", fontsize=13)
        fig.tight_layout()
        if show:
            plt.show()
        else:
            plt.close(fig)

    def draw_static(self, graph, title="Campus Graph", show=True):
        if plt is None:
            raise RuntimeError("matplotlib not installed.")
        fig, ax = plt.subplots(figsize=(10, 8))
        width, height = self._draw_background(ax, graph)
        self._draw_edges(ax, graph)
        self._draw_base_nodes(ax, graph)
        for node in graph.nodes_by_id.values():
            ax.text(node.x + 5, node.y - 5, node.key, fontsize=6, color="#f0f0f0")
        ax.set_title(title)
        ax.set_xlim(0, width)
        ax.set_ylim(height, 0)
        ax.set_xticks([])
        ax.set_yticks([])
        if show:
            plt.show()
        else:
            plt.close(fig)

    def _draw_edges(self, ax, graph):
        for from_id, neighbors in graph.adjacency.items():
            from_node = graph.nodes_by_id[from_id]
            for to_id, _cost in neighbors:
                if to_id < from_id:
                    continue
                to_node = graph.nodes_by_id[to_id]
                ax.plot([from_node.x, to_node.x], [from_node.y, to_node.y],
                        color="#9ca3af", linewidth=1.0, alpha=0.6, zorder=2)

    def _draw_base_nodes(self, ax, graph):
        xs = [n.x for n in graph.nodes_by_id.values()]
        ys = [n.y for n in graph.nodes_by_id.values()]
        colors = ["#2563eb" if n.type == "L" else "#14b8a6" for n in graph.nodes_by_id.values()]
        ax.scatter(xs, ys, c=colors, s=25, edgecolors="white", linewidths=0.4, zorder=3)

    def _mark_nodes(self, ax, graph, node_keys, color, size, label, marker="o"):
        xs, ys = [], []
        for key in node_keys:
            if key in graph.node_id_by_key:
                n = graph.nodes_by_id[graph.node_id(key)]
                xs.append(n.x)
                ys.append(n.y)
        if xs:
            ax.scatter(xs, ys, c=color, s=size, zorder=7, label=label,
                       marker=marker, edgecolors="white", linewidths=0.5)

    def _draw_background(self, ax, graph):
        ax.set_facecolor("#0b1220")
        if mpimg is not None and self.map_image_path.exists():
            try:
                img = mpimg.imread(self.map_image_path)
                h, w = img.shape[0], img.shape[1]
                ax.imshow(img, extent=[0, w, h, 0], zorder=1)
                return float(w), float(h)
            except Exception:
                pass
        max_x = max(n.x for n in graph.nodes_by_id.values()) + 80
        max_y = max(n.y for n in graph.nodes_by_id.values()) + 80
        return max_x, max_y
