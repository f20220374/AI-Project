# AGENTS

Project notes and agent instructions.

# Project: CS F407 AI Assignment – Route Planning System (D3)

## Goal
Build a Python prototype for a multi-stop campus route-planning system on the BITS Pilani vehicle-road graph.

## Assignment requirements
Implement these search algorithms from scratch:
1. BFS
2. UCS
3. Greedy Best-First Search
4. A* Search

Implement these heuristics:
1. nearest_remaining_distance
2. mst_plus_connectors

Include:
- visualization of the search process
- clear README with setup instructions
- algorithm comparison metrics
- easy / medium / hard demo scenarios

You may use standard libraries like:
- heapq
- math
- time
- json
- collections
- tkinter or pygame or matplotlib for visualization

Do NOT use external search/pathfinding libraries for the algorithms.

## Problem model
- Graph is defined in `data/campus_graph.json`
- Campus image in `assets/campus_map.png` is for visualization only
- Start node is fixed: `Main_Gate`
- Each job is a pickup-delivery request: `(pickup_node, drop_node)`
- Requests with `pickup_node = Main_Gate` represent initial deliveries
- Requests with pickup elsewhere represent in-campus pickup/drop jobs
- Vehicle capacity = 2
- Pickup happens automatically when the vehicle reaches a valid pickup node and capacity allows
- Drop happens automatically when the vehicle reaches the matching drop node
- Goal state = all requests delivered
- No return to Main_Gate required after the final delivery

## Search behavior
- BFS runs on an unweighted version of the graph where each edge has cost 1
- UCS, Greedy, and A* run on weighted edges using the graph distances
- Even for BFS, show the final real weighted route cost in output metrics for comparison

## State representation
Use a state with:
- current_node
- carrying
- picked
- delivered

Keep the state hashable and efficient.

## Heuristic guidance
### 1. nearest_remaining_distance
Admissible lower bound based on distance from the current node to the nearest valid remaining service node.

### 2. mst_plus_connectors
Admissible lower bound based on:
- connector from current node to the remaining relevant nodes
- MST cost over remaining relevant nodes

Use graph shortest-path distances between relevant nodes.

## Visualization requirements
Need a visual interface that can:
- show campus map background
- overlay graph nodes/edges
- let the user select or load a scenario
- run one selected algorithm
- animate exploration
- highlight final route
- show metrics:
  - weighted path cost
  - hops
  - nodes expanded
  - runtime
  - max frontier size

Also include a comparison mode that runs all four algorithms on the same scenario.

## Code structure expectations
Suggested modules:
- graph.py
- state.py
- heuristics.py
- algorithms/
- scenarios/
- ui/
- main.py

## Engineering rules
- Keep code modular and readable
- Add docstrings
- Avoid giant files
- Prefer pure functions for algorithms
- Write code that is demo-ready
- Update README with setup and usage steps
- Create sample easy / medium / hard scenarios if not present