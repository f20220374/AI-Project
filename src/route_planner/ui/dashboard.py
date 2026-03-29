from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from route_planner.io.loaders import load_graph, load_scenario, validate_scenario_against_graph
from route_planner.ui.app import RoutePlannerApp, format_metrics_table


class VisualizerDashboard:
    """Interactive control panel for running and visualizing route-planning searches."""

    def __init__(self, graph_path: Path, scenarios_dir: Path) -> None:
        self.project_root = Path(__file__).resolve().parents[3]
        self.graph_path = self._resolve_graph_path(graph_path)
        self.scenarios_dir = self._resolve_scenarios_dir(scenarios_dir)
        self.app = RoutePlannerApp()

        self.root = tk.Tk()
        self.root.title("AI Route Planner · Visualizer")
        self.root.geometry("980x700")
        self.root.minsize(900, 620)

        self.current_graph = None

        self._init_style()
        self._build_layout()
        self._load_scenarios_into_dropdown()

    def _resolve_graph_path(self, graph_path: Path) -> Path:
        candidate = Path(graph_path).expanduser()
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve()
        if candidate.exists():
            return candidate

        fallback = self.project_root / "data" / "campus_graph.json"
        return fallback

    def _resolve_scenarios_dir(self, scenarios_dir: Path) -> Path:
        candidate = Path(scenarios_dir).expanduser()
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve()
        if candidate.exists() and candidate.is_dir():
            return candidate

        fallback = self.project_root / "scenarios"
        return fallback

    def run(self) -> None:
        self.root.mainloop()

    def _init_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        bg = "#0f172a"
        panel = "#111827"
        fg = "#e5e7eb"
        accent = "#3b82f6"

        self.root.configure(bg=bg)

        style.configure("App.TFrame", background=bg)
        style.configure("Card.TFrame", background=panel)
        style.configure("Title.TLabel", background=bg, foreground="#f8fafc", font=("Helvetica", 18, "bold"))
        style.configure("Hint.TLabel", background=bg, foreground="#94a3b8", font=("Helvetica", 10))
        style.configure("Card.TLabel", background=panel, foreground=fg, font=("Helvetica", 10))
        style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=8)
        style.map("Action.TButton", background=[("active", accent)])

    def _build_layout(self) -> None:
        outer = ttk.Frame(self.root, style="App.TFrame", padding=18)
        outer.pack(fill=tk.BOTH, expand=True)

        ttk.Label(outer, text="Campus Route Planner", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            outer,
            text="Choose scenario + algorithm, then run animated search or compare all algorithms.",
            style="Hint.TLabel",
        ).pack(anchor=tk.W, pady=(2, 14))

        controls = ttk.Frame(outer, style="Card.TFrame", padding=14)
        controls.pack(fill=tk.X)

        self.scenario_var = tk.StringVar()
        self.algorithm_var = tk.StringVar(value="astar")
        self.heuristic_var = tk.StringVar(value="mst")
        self.visualize_var = tk.BooleanVar(value=True)
        self.show_route_var = tk.BooleanVar(value=True)
        self.delay_var = tk.DoubleVar(value=0.02)

        self.scenario_combo = self._labeled_combobox(
            controls,
            row=0,
            col=0,
            label="Scenario",
            var=self.scenario_var,
            values=[],
        )
        self._labeled_combobox(
            controls,
            row=0,
            col=1,
            label="Algorithm",
            var=self.algorithm_var,
            values=["bfs", "ucs", "greedy", "astar"],
        )
        self._labeled_combobox(
            controls,
            row=0,
            col=2,
            label="Heuristic",
            var=self.heuristic_var,
            values=["nearest", "mst"],
        )

        ttk.Checkbutton(controls, text="Animate search", variable=self.visualize_var).grid(
            row=1, column=0, sticky=tk.W, padx=8, pady=(10, 0)
        )
        ttk.Checkbutton(controls, text="Show final route map", variable=self.show_route_var).grid(
            row=2, column=0, sticky=tk.W, padx=8, pady=(8, 0)
        )

        ttk.Label(controls, text="Animation delay (sec)", style="Card.TLabel").grid(
            row=1, column=1, sticky=tk.W, padx=8, pady=(10, 0)
        )
        delay_scale = ttk.Scale(
            controls,
            from_=0.0,
            to=0.15,
            variable=self.delay_var,
            orient=tk.HORIZONTAL,
            length=220,
        )
        delay_scale.grid(row=1, column=2, sticky=tk.W, padx=8, pady=(10, 0))

        button_row = ttk.Frame(outer, style="App.TFrame")
        button_row.pack(fill=tk.X, pady=(12, 10))

        ttk.Button(button_row, text="Run Selected", style="Action.TButton", command=self._run_selected).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(button_row, text="Compare All", style="Action.TButton", command=self._run_compare).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(button_row, text="Show Graph", style="Action.TButton", command=self._show_graph).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(button_row, text="Clear", style="Action.TButton", command=self._clear_output).pack(side=tk.LEFT)

        content = ttk.Panedwindow(outer, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(content, style="Card.TFrame", padding=10)
        right_panel = ttk.Frame(content, style="Card.TFrame", padding=10)
        content.add(left_panel, weight=3)
        content.add(right_panel, weight=5)

        output_card = left_panel

        ttk.Label(output_card, text="Run Output", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 8))

        self.output = tk.Text(
            output_card,
            wrap=tk.WORD,
            bg="#0b1220",
            fg="#d1d5db",
            insertbackground="#e5e7eb",
            font=("Menlo", 11),
            relief=tk.FLAT,
            padx=10,
            pady=10,
        )
        self.output.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right_panel, text="Live Map", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self.figure = Figure(figsize=(6.2, 5.2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(2, weight=1)

    def _labeled_combobox(
        self,
        parent: ttk.Frame,
        row: int,
        col: int,
        label: str,
        var: tk.StringVar,
        values: list[str],
    ) -> ttk.Combobox:
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row, column=col, sticky=tk.W, padx=8, pady=(0, 6))
        combo = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", width=28)
        combo.grid(row=row + 1, column=col, sticky=tk.EW, padx=8)
        return combo

    def _load_scenarios_into_dropdown(self) -> None:
        scenario_files = sorted(path.name for path in self.scenarios_dir.glob("*.json"))
        if not scenario_files:
            messagebox.showerror(
                "No scenarios",
                "No .json files found in scenarios directory.\n"
                f"Resolved scenarios path: {self.scenarios_dir}\n"
                f"Resolved graph path: {self.graph_path}",
            )
            return

        self.scenario_combo.configure(values=scenario_files)
        self.scenario_var.set(scenario_files[0])

    def _current_inputs(self):
        scenario_file = self.scenario_var.get().strip()
        if not scenario_file:
            raise ValueError("Please choose a scenario.")

        graph = load_graph(self.graph_path)
        scenario = load_scenario(self.scenarios_dir / scenario_file)
        errors = validate_scenario_against_graph(scenario, graph)
        if errors:
            raise ValueError("Scenario validation failed:\n- " + "\n- ".join(errors))

        self.app.config.animation_delay_seconds = float(self.delay_var.get())
        self.current_graph = graph
        return graph, scenario

    def _run_selected(self) -> None:
        try:
            graph, scenario = self._current_inputs()
            result = self.app.run_single(
                graph=graph,
                scenario=scenario,
                algorithm=self.algorithm_var.get(),
                heuristic_name=self.heuristic_var.get(),
                visualize=False,
            )
            self._draw_embedded_map(
                graph=graph,
                explored_nodes=result.explored_nodes if bool(self.visualize_var.get()) else None,
                node_path=result.node_path if bool(self.show_route_var.get()) else None,
                title=f"{result.algorithm} · {scenario.name}",
            )
            route_pretty = self._numbered_route(result.node_path)
            self._append_output(
                f"[{result.algorithm}] solved={result.solved}\n"
                f"Path: {' -> '.join(result.node_path) if result.node_path else '(none)'}\n"
                f"Route steps:\n{route_pretty}\n"
                f"weighted path cost: {result.metrics.weighted_path_cost:.1f}\n"
                f"hops: {result.metrics.hops}\n"
                f"nodes expanded: {result.metrics.nodes_expanded}\n"
                f"runtime (ms): {result.metrics.runtime_ms:.2f}\n"
                f"max frontier size: {result.metrics.max_frontier_size}\n"
            )
        except Exception as exc:
            messagebox.showerror("Run failed", str(exc))

    def _run_compare(self) -> None:
        try:
            graph, scenario = self._current_inputs()
            results = self.app.run_comparison(
                graph=graph,
                scenario=scenario,
                heuristic_name=self.heuristic_var.get(),
                visualize=False,
            )
            self._append_output("Comparison metrics\n" + format_metrics_table(results) + "\n")
            solved_results = [result for result in results if result.solved and result.node_path]
            if solved_results:
                best = min(solved_results, key=lambda result: result.metrics.weighted_path_cost)
                self._draw_embedded_map(
                    graph=graph,
                    explored_nodes=best.explored_nodes if bool(self.visualize_var.get()) else None,
                    node_path=best.node_path if bool(self.show_route_var.get()) else None,
                    title=f"Best route in compare: {best.algorithm}",
                )
        except Exception as exc:
            messagebox.showerror("Comparison failed", str(exc))

    def _show_graph(self) -> None:
        try:
            graph = load_graph(self.graph_path)
            self.current_graph = graph
            self._draw_embedded_map(
                graph=graph,
                explored_nodes=None,
                node_path=None,
                title="Campus Graph (Labeled)",
                show_labels=True,
            )
        except Exception as exc:
            messagebox.showerror("Graph view failed", str(exc))

    def _clear_output(self) -> None:
        self.output.delete("1.0", tk.END)

    def _append_output(self, text: str) -> None:
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def _draw_embedded_map(
        self,
        graph,
        explored_nodes: list[str] | None,
        node_path: list[str] | None,
        title: str,
        show_labels: bool = False,
    ) -> None:
        self.ax.clear()

        width, height = self._draw_background(graph)

        for from_id, neighbors in graph.adjacency.items():
            from_node = graph.nodes_by_id[from_id]
            for to_id, _cost in neighbors:
                if to_id < from_id:
                    continue
                to_node = graph.nodes_by_id[to_id]
                self.ax.plot(
                    [from_node.x, to_node.x],
                    [from_node.y, to_node.y],
                    color="#6b7280",
                    linewidth=1,
                    alpha=0.55,
                    zorder=2,
                )

        xs = [node.x for node in graph.nodes_by_id.values()]
        ys = [node.y for node in graph.nodes_by_id.values()]
        self.ax.scatter(xs, ys, c="#93c5fd", s=20, edgecolors="white", linewidths=0.4, zorder=3)

        if show_labels:
            for node in graph.nodes_by_id.values():
                self.ax.text(
                    node.x + 5,
                    node.y - 5,
                    node.key,
                    fontsize=7,
                    color="#f8fafc",
                    zorder=7,
                    bbox={"facecolor": "#111827", "alpha": 0.55, "edgecolor": "none", "pad": 1},
                )

        if explored_nodes:
            explored_ids = [graph.node_id(node) for node in explored_nodes if node in graph.node_id_by_key]
            if explored_ids:
                ex = [graph.nodes_by_id[node_id].x for node_id in explored_ids]
                ey = [graph.nodes_by_id[node_id].y for node_id in explored_ids]
                self.ax.scatter(ex, ey, c="#f59e0b", s=26, alpha=0.8, zorder=4, label="Explored")

        if node_path and len(node_path) >= 2:
            route_ids = [graph.node_id(node) for node in node_path if node in graph.node_id_by_key]
            rx = [graph.nodes_by_id[node_id].x for node_id in route_ids]
            ry = [graph.nodes_by_id[node_id].y for node_id in route_ids]
            self.ax.plot(rx, ry, color="#ef4444", linewidth=3.2, zorder=5, label="Final route")
            self.ax.scatter([rx[0]], [ry[0]], c="#22c55e", s=60, zorder=6)
            self.ax.scatter([rx[-1]], [ry[-1]], c="#e11d48", s=60, zorder=6)

        self.ax.set_title(title, fontsize=11)
        self.ax.set_xlim(0, width)
        self.ax.set_ylim(height, 0)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_facecolor("#0b1220")

        handles, labels = self.ax.get_legend_handles_labels()
        if handles:
            self.ax.legend(loc="lower right", fontsize=9)

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _draw_background(self, graph) -> tuple[float, float]:
        try:
            if self.app.renderer.map_image_path.exists():
                image = mpimg.imread(self.app.renderer.map_image_path)
                height, width = image.shape[0], image.shape[1]
                self.ax.imshow(image, extent=[0, width, height, 0], zorder=1)
                return float(width), float(height)
        except Exception:
            pass

        max_x = max(node.x for node in graph.nodes_by_id.values()) + 80
        max_y = max(node.y for node in graph.nodes_by_id.values()) + 80
        return max_x, max_y

    @staticmethod
    def _numbered_route(node_path: list[str]) -> str:
        if not node_path:
            return "(none)"
        return "\n".join(f"{index + 1:02d}. {node}" for index, node in enumerate(node_path))
