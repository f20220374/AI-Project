# CS F407 AI Assignment — Route Planner (Project 3, L2)

Campus pickup-delivery route planner on the BITS Pilani vehicle-road graph.
Implements BFS, UCS, Greedy, and A* on an augmented state space.

---

## How the graph was made

The campus graph (`data/campus_graph.json`) was built using the campus map image (`assets/campus_map.png`).
We used an AI tool to identify node positions and rough distances from the image, then went through
the JSON by hand to fix coordinates, remove pedestrian-only paths (NAB rotunda, Snake Path, hostel stairways),
and double-check edge weights against known distances. So the base was AI-assisted but the final graph
is manually verified.

The visualization UI (`src/route_planner/ui/`) was also scaffolded with an AI tool and then adjusted to
fit what we needed — color coding, the embedded tkinter dashboard, and the side-by-side compare view.

The search algorithms, heuristics, problem formulation, and state model were written by us from scratch.

---

## Features

- 4 search algorithms written from scratch:
  - BFS (unit edge costs)
  - UCS (weighted, optimal)
  - Greedy Best-First (heuristic only, fast but not optimal)
  - A* (optimal, uses either h1 or h2)
- 2 admissible heuristics:
  - `nearest_remaining_distance` (h1)
  - `mst_plus_connectors` (h2, dominates h1)
- State: `(current_node, carrying, picked, delivered)`
- Auto pickup/drop at each node with capacity=2
- Visualization on top of the actual campus map:
  - green star = start
  - blue triangles = pickup nodes
  - red triangles = drop nodes
  - grey dots = explored nodes
  - yellow line = final path
- Animated search + side-by-side algorithm comparison
- Interactive desktop UI (tkinter + matplotlib)
- Metrics per run: cost, hops, nodes expanded, runtime, max frontier size

---

## Project structure

```
repo_clone/
  assets/
    campus_map.png          (background image, visualization only)
  data/
    campus_graph.json       (48 nodes, ~75 edges, manually verified)
  scenarios/
    easy.json               (2 requests)
    medium.json             (3 requests, one in-campus pickup)
    hard.json               (5 requests, mixed zones)
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
      dashboard.py
      renderer.py
    heuristics.py
    main.py
  main.py
  requirements.txt
  README.md
```

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No external search or pathfinding library is used for the algorithms.

---

## Usage

### List available scenarios

```bash
python3 main.py --list-scenarios
```

### Run a single algorithm

```bash
python3 main.py --scenario easy.json --mode single --algorithm astar --heuristic mst
```

### Compare all algorithms

```bash
python3 main.py --scenario hard.json --mode compare --heuristic mst
```

### With visualization (animated map)

```bash
python3 main.py --scenario medium.json --mode compare --visualize --delay 0.02
```

### Interactive UI

```bash
python3 main.py --mode ui
```

This opens a desktop control panel with:
- difficulty / case / algorithm / heuristic dropdowns
- Run Selected (single algorithm)
- Compare All (BFS/UCS/Greedy/A*)
- Run All Cases (batch benchmark over selected difficulty or all)
- optional animation toggle + delay slider
- metrics + route output inside the dashboard

### Scenario case bank

- Easy: `easy_01.json` ... `easy_10.json`
- Medium: `medium_01.json` ... `medium_10.json`
- Hard: `hard_01.json` ... `hard_10.json`

When you use **Run All Cases**, the dashboard reports per-algorithm aggregate stats:
- average/min/max weighted path cost
- average/min/max nodes expanded
- average/min/max runtime
- solved ratio

### Visualization / animation

---

## Behavior notes

- `data/campus_graph.json` is the only search graph used — the PNG is for display only.
- BFS searches with unit edge costs but the output still shows the real weighted path cost.
- Goal = all requests delivered. No need to return to start.
- Drop happens before pickup at each node (so a slot frees up before a new item is loaded).
