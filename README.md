# Mini-Courier Planner

A Python prototype that combines **Merge Sort, 0/1 Knapsack Dynamic Programming, Dijkstra's shortest-path algorithm, and a Nearest-Neighbour TSP approximation** to plan parcel selection and delivery routes.

## Problem statement

Given a collection of parcels and a weighted road network, the system:
1. Prioritizes parcels by priority, deadline, and value-to-weight ratio.
2. Selects a high-value subset that fits within a vehicle's weight capacity.
3. Finds shortest road paths from the depot to selected delivery locations.
4. Builds an approximate multi-stop delivery tour and calculates its distance.
5. Benchmarks the main algorithmic components on increasing input sizes.

> **Objective distinction:** Merge Sort establishes a priority-oriented processing order. The Knapsack DP independently maximizes total parcel value subject to the vehicle capacity. The current DP objective does not mathematically maximize priority or minimize lateness.

## Project structure

```text
Mini-Courier-Planner/
├── mini_courier_planner.ipynb    # Main end-to-end implementation and outputs
├── src/
│   ├── __init__.py
│   ├── sorting.py                # Merge Sort
│   ├── knapsack.py               # 0/1 Knapsack DP
│   ├── dijkstra.py               # Graph loading, Dijkstra, graph visualization
│   ├── tsp.py                    # Nearest-Neighbour route approximation
│   ├── performance.py            # Runtime benchmark (input sizes 10-100)
│   └── analysis.py               # Correctness tests, algorithm comparisons, large benchmark, route image
├── datasets/
│   ├── parcels.csv               # Sample parcel dataset
│   └── roads.csv                 # Weighted undirected road dataset
├── images/
│   ├── road_graph.png
│   ├── route_map.png
│   ├── runtime_comparison.png
│   ├── runtime_results.csv
│   ├── runtime_large.png
│   ├── runtime_large.csv
│   └── screenshots/              # Notebook output screenshots
│       ├── 2_packing_plan_and_sorted_parcels.png
│       ├── 2_dp_table_and_result.png
│       ├── final_route.png
│       └── tests_and_comparisons.png
├── requirements.txt
└── .gitignore
```

## Requirements

- Python 3.10 or newer
- Jupyter Notebook
- Matplotlib

Install dependencies:

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Execution Steps

Run commands from the project root directory (the directory containing this README).

### Option 1: Run the complete notebook

```bash
jupyter notebook mini_courier_planner.ipynb
```

Open the notebook and choose **Kernel → Restart Kernel and Run All Cells**. The notebook loads the CSV datasets, displays the graph, performs parcel prioritization and packing, prints shortest paths, and generates the final delivery route.

### Option 2: Run the performance benchmark

```bash
python -m src.performance
```

This benchmarks input sizes 10, 25, 50, and 100. It writes:
- `images/runtime_results.csv`
- `images/runtime_comparison.png`

Runtime values vary by hardware, Python version, and system load. Re-run the benchmark on the machine used for the final demonstration if updated measurements are required.

### Option 3: Run tests, comparisons and the large benchmark
```bash
python -m src.analysis
```
This runs four correctness checks (Merge Sort vs sorted(), Knapsack vs brute force, Dijkstra vs Floyd-Warshall, route length) compares the chosen algorithms with alternatives (Bubble Sort, greedy knapsack, brute-force TSP), benchmarks input sizes 100, 200, 500 and 1000 and draws the final route. It writes:

- `images/runtime_large.csv`
- `images/runtime_large.png`
- `images/route_map.png`

## Sample result

With the supplied sample data and vehicle capacity of 15 kg, the notebook selects five parcels:

`P03, P01, P09, P08, P05`

- Packed weight: 15 kg
- Total parcel value: 325
- Selected delivery locations: A, B, C
- Approximate delivery tour: D0 → C → A → B → D0
- Route distance: 18 km

The route is an approximation produced by Nearest Neighbour; it is not guaranteed to be the globally shortest TSP tour.

## Algorithms and complexity

Let `n` be the number of parcels, `W` the integer vehicle capacity, `V` the number of graph vertices, and `E` the number of graph edges.

| Component | Algorithm | Time complexity |
|---|---|---|
| Parcel prioritization | Merge Sort | `O(n log n)` |
| Packing | 0/1 Knapsack DP | `O(nW)` |
| One-source shortest paths | Dijkstra with a binary heap | `O((V + E) log V)` |
| Multi-stop route | Nearest Neighbour with repeated Dijkstra | `O(V(V + E) log V)` upper bound |

The DP table uses `O(nW)` space. Merge Sort uses `O(n)` auxiliary space. Dijkstra uses `O(V + E)` graph/auxiliary storage. The route output itself may contain repeated intermediate road vertices.



## Assumptions and limitations

- Road distances are non-negative and the supplied road network is undirected.
- Parcel weights and vehicle capacity are integer values because the DP table is indexed by integer capacity.
- The current packing objective maximizes parcel value; priority and deadline affect sorting order, not the DP objective.
- A delivery location is visited once even if multiple selected parcels share that destination.
- The Nearest-Neighbour route is a heuristic and may not be globally optimal.
- The sample deadlines are illustrative dataset values, not live delivery commitments.
