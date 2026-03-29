# AI-Project

Python prototype for multi-stop campus pickup-delivery planning on the BITS Pilani vehicle-road graph.

## Features

- Search algorithms implemented from scratch:
	- BFS (unweighted expansion)
	- UCS (weighted)
	- Greedy Best-First Search (weighted + heuristic)
	- A* (weighted + heuristic)
- Heuristics:
	- `nearest_remaining_distance`
	- `mst_plus_connectors`
- State representation:
	- `current_node`, `carrying`, `picked`, `delivered`
- Automatic pickup/drop semantics with capacity handling
- Visualization with campus map background and graph overlay
- Animated exploration + final route highlighting
- Comparison mode running all 4 algorithms on the same scenario
- Metrics shown per run:
	- weighted path cost
	- hops
	- nodes expanded
	- runtime
	- max frontier size

## Project structure

```
ai-route-planner/
	assets/
		campus_map.png
	data/
		campus_graph.json
	scenarios/
		easy.json
		medium.json
		hard.json
	src/route_planner/
		algorithms/
			astar.py
			bfs.py
			common.py
			greedy.py
			ucs.py
		core/
			metrics.py
			problem.py
		io/
			loaders.py
		models/
			graph.py
			scenario.py
			state.py
		ui/
			app.py
			renderer.py
		heuristics.py
		main.py
	main.py
	pyproject.toml
	AGENTS.md
	README.md
```

## Setup

From project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib
```

No external search/pathfinding library is used.

## Usage

### List scenarios

```bash
python3 main.py --list-scenarios
```

### Single algorithm run

```bash
python3 main.py --scenario easy.json --mode single --algorithm astar --heuristic mst
```

### Compare all algorithms on one scenario

```bash
python3 main.py --scenario hard.json --mode compare --heuristic nearest
```

### Interactive visualizer dashboard

```bash
python3 main.py --mode ui
```

This opens a desktop control panel with:
- scenario / algorithm / heuristic dropdowns
- Run Selected (single algorithm)
- Compare All (BFS/UCS/Greedy/A*)
- optional animation toggle + delay slider
- metrics + route output inside the dashboard

### Visualization / animation

Add `--visualize` to `single` or `compare` mode:

```bash
python3 main.py --scenario medium.json --mode single --algorithm ucs --visualize --delay 0.02
```

## Notes on behavior

- `data/campus_graph.json` is the only authoritative search graph.
- `assets/campus_map.png` is visualization-only.
- BFS expands using unit edge costs; all runs still report final weighted route cost from graph edge weights.
- Goal state is when all requests are delivered; no return to `Main_Gate` is required.
