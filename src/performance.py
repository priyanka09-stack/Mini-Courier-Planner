
"""
Phase 4: Performance Testing and Optimization
Mini-Courier Planner

Run from the project root:
    python -m src.performance
"""

import csv
import os
import random
import statistics
import time

import matplotlib.pyplot as plt

from src.sorting import sort_parcels
from src.knapsack import knapsack
from src.dijkstra import dijkstra
from src.tsp import delivery_route


OUTPUT_DIR = "images"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_parcels(n, seed=42):
    """Generate reproducible sample parcel data."""
    rng = random.Random(seed + n)
    parcels = []

    for i in range(n):
        parcels.append({
            "id": f"P{i + 1}",
            "destination": f"N{(i % n) + 1}",
            "weight": rng.randint(1, 10),
            "value": rng.randint(50, 500),
            "priority": rng.randint(1, 5),
            "deadline": rng.randint(1, 30),
        })

    return parcels


def generate_graph(n):
    """Create a connected weighted graph for benchmarking."""
    graph = {}
    nodes = ["D0"] + [f"N{i}" for i in range(1, n + 1)]

    for node in nodes:
        graph[node] = []

    # Connect neighbouring nodes in a chain.
    for i in range(len(nodes) - 1):
        a, b = nodes[i], nodes[i + 1]
        graph[a].append((b, 2.0))
        graph[b].append((a, 2.0))

    # Add shortcuts to make the graph more realistic.
    for i in range(len(nodes) - 2):
        a, b = nodes[i], nodes[i + 2]
        graph[a].append((b, 3.0))
        graph[b].append((a, 3.0))

    return graph


def measure_ms(function, *args):
    """Return execution time in milliseconds."""
    start = time.perf_counter()
    function(*args)
    return (time.perf_counter() - start) * 1000


def benchmark():
    sizes = [10, 25, 50, 100]
    results = []

    for n in sizes:
        parcels = generate_parcels(n)
        graph = generate_graph(n)

        # Keep capacity proportional to dataset size.
        capacity = max(15, n * 3)

        # Use the same inputs for repeated measurements.
        sort_times = []
        knapsack_times = []
        dijkstra_times = []
        route_times = []

        for _ in range(3):
            sort_times.append(
                measure_ms(sort_parcels, parcels)
            )

            knapsack_times.append(
                measure_ms(knapsack, parcels, capacity)
            )

            dijkstra_times.append(
                measure_ms(dijkstra, graph, "D0")
            )

            destinations = [
                f"N{i}" for i in range(1, n + 1)
            ]

            route_times.append(
                measure_ms(
                    delivery_route, graph, "D0", destinations
                )
            )

        row = {
            "input_size": n,
            "capacity": capacity,
            "sorting_ms": statistics.median(sort_times),
            "knapsack_ms": statistics.median(knapsack_times),
            "dijkstra_ms": statistics.median(dijkstra_times),
            "routing_ms": statistics.median(route_times),
        }

        results.append(row)

        print(f"\nInput size: {n}")
        for name, value in row.items():
            if name.endswith("_ms"):
                print(f"{name}: {value:.4f} ms")

    # Save experimental measurements.
    csv_path = os.path.join(OUTPUT_DIR, "runtime_results.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    # Plot the measured execution times.
    plt.figure(figsize=(10, 6))

    for column in (
        "sorting_ms",
        "knapsack_ms",
        "dijkstra_ms",
        "routing_ms",
    ):
        plt.plot(
            [row["input_size"] for row in results],
            [row[column] for row in results],
            marker="o",
            label=column.replace("_ms", "").title(),
        )

    plt.xlabel("Input size (number of parcels / delivery nodes)")
    plt.ylabel("Median execution time (milliseconds)")
    plt.title("Mini-Courier Planner: Runtime Comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    chart_path = os.path.join(OUTPUT_DIR, "runtime_comparison.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()

    print(f"\nResults saved to: {csv_path}")
    print(f"Runtime chart saved to: {chart_path}")


if __name__ == "__main__":
    benchmark()
