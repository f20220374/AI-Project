from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from route_planner.io.loaders import load_graph, load_scenario, validate_scenario_against_graph
from route_planner.ui.app import RoutePlannerApp, format_metrics_table


class VisualizerDashboard:

    def __init__(self, graph_path, scenarios_dir):
        self.project_root = Path(__file__).resolve().parents[3]
        self.graph_path = self._resolve_path(graph_path, self.project_root / "data" / "campus_graph.json")
        self.scenarios_dir = self._resolve_dir(scenarios_dir, self.project_root / "scenarios")
        self.app = RoutePlannerApp()
        self.current_scenario = None

        self.root = tk.Tk()
        self.root.title("Campus Route Planner")
        self.root.geometry("980x700")
        self.root.minsize(900, 620)

        self._init_style()
        self._build_layout()
        self._load_scenarios()

    def _resolve_path(self, path, fallback):
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        return p if p.exists() else fallback

    def _resolve_dir(self, path, fallback):
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        return p if (p.exists() and p.is_dir()) else fallback

    def run(self):
        self.root.mainloop()

    def _init_style(self):
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

    def _build_layout(self):
        outer = ttk.Frame(self.root, style="App.TFrame", padding=18)
        outer.pack(fill=tk.BOTH, expand=True)

        ttk.Label(outer, text="Campus Route Planner", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            outer,
            text="Pick a scenario and algorithm, then run or compare.",
            style="Hint.TLabel",
        ).pack(anchor=tk.W, pady=(2, 14))

        controls = ttk.Frame(outer, style="Card.TFrame", padding=14)
        controls.pack(fill=tk.X)

        self.scenario_var = tk.StringVar()
        self.algorithm_var = tk.StringVar(value="astar")
        self.heuristic_var = tk.StringVar(value="mst")
        self.show_explored_var = tk.BooleanVar(value=True)
        self.show_route_var = tk.BooleanVar(value=True)
        self.delay_var = tk.DoubleVar(value=0.02)

        self.scenario_combo = self._labeled_combo(controls, 0, 0, "Scenario", self.scenario_var, [])
        self._labeled_combo(controls, 0, 1, "Algorithm", self.algorithm_var, ["bfs", "ucs", "greedy", "astar"])
        self._labeled_combo(controls, 0, 2, "Heuristic", self.heuristic_var, ["nearest", "mst"])

        ttk.Checkbutton(controls, text="Show explored nodes", variable=self.show_explored_var).grid(
            row=1, column=0, sticky=tk.W, padx=8, pady=(10, 0))
        ttk.Checkbutton(controls, text="Show final route", variable=self.show_route_var).grid(
            row=2, column=0, sticky=tk.W, padx=8, pady=(8, 0))

        ttk.Label(controls, text="Animation delay (sec)", style="Card.TLabel").grid(
            row=1, column=1, sticky=tk.W, padx=8, pady=(10, 0))
        ttk.Scale(controls, from_=0.0, to=0.15, variable=self.delay_var,
                  orient=tk.HORIZONTAL, length=220).grid(row=1, column=2, sticky=tk.W, padx=8, pady=(10, 0))

        btns = ttk.Frame(outer, style="App.TFrame")
        btns.pack(fill=tk.X, pady=(12, 10))
        ttk.Button(btns, text="Run Selected", style="Action.TButton", command=self._run_selected).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="Compare All", style="Action.TButton", command=self._run_compare).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="Show Graph", style="Action.TButton", command=self._show_graph).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="Clear", style="Action.TButton", command=self._clear).pack(side=tk.LEFT)

        content = ttk.Panedwindow(outer, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(content, style="Card.TFrame", padding=10)
        right = ttk.Frame(content, style="Card.TFrame", padding=10)
        content.add(left, weight=3)
        content.add(right, weight=5)

        ttk.Label(left, text="Run Output", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self.output = tk.Text(left, wrap=tk.WORD, bg="#0b1220", fg="#d1d5db",
                              insertbackground="#e5e7eb", font=("Menlo", 11),
                              relief=tk.FLAT, padx=10, pady=10)
        self.output.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Map", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self.figure = Figure(figsize=(6.2, 5.2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(2, weight=1)

    def _labeled_combo(self, parent, row, col, label, var, values):
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row, column=col, sticky=tk.W, padx=8, pady=(0, 6))
        combo = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", width=28)
        combo.grid(row=row + 1, column=col, sticky=tk.EW, padx=8)
        return combo

    def _load_scenarios(self):
        files = sorted(p.name for p in self.scenarios_dir.glob("*.json"))
        if not files:
            messagebox.showerror("No scenarios", f"No .json files in {self.scenarios_dir}")
            return
        self.scenario_combo.configure(values=files)
        self.scenario_var.set(files[0])

    def _load_inputs(self):
        fname = self.scenario_var.get().strip()
        if not fname:
            raise ValueError("Choose a scenario first.")
        graph = load_graph(self.graph_path)
        scenario = load_scenario(self.scenarios_dir / fname)
        errors = validate_scenario_against_graph(scenario, graph)
        if errors:
            raise ValueError("Scenario errors:\n- " + "\n- ".join(errors))
        self.app.config.animation_delay_seconds = float(self.delay_var.get())
        self.current_scenario = scenario
        return graph, scenario

    def _run_selected(self):
        try:
            graph, scenario = self._load_inputs()
            result = self.app.run_single(
                graph=graph, scenario=scenario,
                algorithm=self.algorithm_var.get(),
                heuristic_name=self.heuristic_var.get(),
                visualize=False,
            )
            self._draw_map(graph, scenario,
                           explored=result.explored_nodes if self.show_explored_var.get() else None,
                           path=result.node_path if self.show_route_var.get() else None,
                           title=f"{result.algorithm} - {scenario.name}")
            self._append(
                f"[{result.algorithm}] solved={result.solved}\n"
                f"Path: {' -> '.join(result.node_path) if result.node_path else '(none)'}\n"
                f"Steps:\n{self._format_route(result.node_path)}\n"
                f"cost: {result.metrics.weighted_path_cost:.1f}\n"
                f"hops: {result.metrics.hops}\n"
                f"expanded: {result.metrics.nodes_expanded}\n"
                f"runtime: {result.metrics.runtime_ms:.2f}ms\n"
                f"max frontier: {result.metrics.max_frontier_size}\n"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _run_compare(self):
        try:
            graph, scenario = self._load_inputs()
            results = self.app.run_comparison(
                graph=graph, scenario=scenario,
                heuristic_name=self.heuristic_var.get(),
                visualize=False,
            )
            self._append("Comparison\n" + format_metrics_table(results) + "\n")
            # show best result on the map
            solved = [r for r in results if r.solved and r.node_path]
            if solved:
                best = min(solved, key=lambda r: r.metrics.weighted_path_cost)
                self._draw_map(graph, scenario,
                               explored=best.explored_nodes if self.show_explored_var.get() else None,
                               path=best.node_path if self.show_route_var.get() else None,
                               title=f"Best: {best.algorithm}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_graph(self):
        try:
            graph = load_graph(self.graph_path)
            self._draw_map(graph, scenario=None, explored=None, path=None,
                           title="Campus Graph", show_labels=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear(self):
        self.output.delete("1.0", tk.END)

    def _append(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def _draw_map(self, graph, scenario, explored, path, title, show_labels=False):
        self.ax.clear()
        self.ax.set_facecolor("#0b1220")

        # background image
        try:
            if self.app.renderer.map_image_path.exists():
                img = mpimg.imread(self.app.renderer.map_image_path)
                h, w = img.shape[0], img.shape[1]
                self.ax.imshow(img, extent=[0, w, h, 0], zorder=1)
                width, height = float(w), float(h)
            else:
                raise FileNotFoundError
        except Exception:
            width = max(n.x for n in graph.nodes_by_id.values()) + 80
            height = max(n.y for n in graph.nodes_by_id.values()) + 80

        # edges
        for from_id, nbrs in graph.adjacency.items():
            fn = graph.nodes_by_id[from_id]
            for to_id, _ in nbrs:
                if to_id < from_id:
                    continue
                tn = graph.nodes_by_id[to_id]
                self.ax.plot([fn.x, tn.x], [fn.y, tn.y], color="#6b7280", linewidth=1, alpha=0.5, zorder=2)

        # base nodes
        xs = [n.x for n in graph.nodes_by_id.values()]
        ys = [n.y for n in graph.nodes_by_id.values()]
        self.ax.scatter(xs, ys, c="#93c5fd", s=18, edgecolors="white", linewidths=0.3, zorder=3)

        if show_labels:
            for node in graph.nodes_by_id.values():
                self.ax.text(node.x + 4, node.y - 4, node.key, fontsize=6, color="#f0f0f0", zorder=7,
                             bbox={"facecolor": "#111827", "alpha": 0.5, "edgecolor": "none", "pad": 1})

        # grey = explored
        if explored:
            eids = [graph.node_id(n) for n in explored if n in graph.node_id_by_key]
            if eids:
                ex = [graph.nodes_by_id[i].x for i in eids]
                ey = [graph.nodes_by_id[i].y for i in eids]
                self.ax.scatter(ex, ey, c="grey", s=22, alpha=0.7, zorder=4, label="Explored")

        # yellow = path
        if path and len(path) >= 2:
            rids = [graph.node_id(n) for n in path if n in graph.node_id_by_key]
            rx = [graph.nodes_by_id[i].x for i in rids]
            ry = [graph.nodes_by_id[i].y for i in rids]
            self.ax.plot(rx, ry, color="yellow", linewidth=3, zorder=5, label="Path")

        # color-coded special nodes from scenario
        if scenario:
            pickup_nodes = list({r.pickup for r in scenario.requests})
            drop_nodes = list({r.drop for r in scenario.requests})
            self._mark(graph, pickup_nodes, "blue", 70, "Pickup", "^")
            self._mark(graph, drop_nodes, "red", 70, "Drop", "v")
            if scenario.start_node in graph.node_id_by_key:
                nid = graph.node_id(scenario.start_node)
                n = graph.nodes_by_id[nid]
                self.ax.scatter([n.x], [n.y], c="green", s=110, zorder=8, label="Start", marker="*")

        self.ax.set_title(title, fontsize=11)
        self.ax.set_xlim(0, width)
        self.ax.set_ylim(height, 0)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        handles, labels = self.ax.get_legend_handles_labels()
        if handles:
            self.ax.legend(loc="lower right", fontsize=8)

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _mark(self, graph, node_keys, color, size, label, marker):
        xs, ys = [], []
        for key in node_keys:
            if key in graph.node_id_by_key:
                n = graph.nodes_by_id[graph.node_id(key)]
                xs.append(n.x)
                ys.append(n.y)
        if xs:
            self.ax.scatter(xs, ys, c=color, s=size, zorder=7, label=label,
                            marker=marker, edgecolors="white", linewidths=0.5)

    @staticmethod
    def _format_route(node_path):
        if not node_path:
            return "(none)"
        return "\n".join(f"{i + 1:02d}. {n}" for i, n in enumerate(node_path))
