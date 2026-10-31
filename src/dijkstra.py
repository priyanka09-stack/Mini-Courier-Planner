import csv
import heapq

import os
import math
import matplotlib.pyplot as plt

# weighted road graph
def load_graph(filename):
    graph = {}

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            source = row["from"]
            destination = row["to"]
            distance = float(row["distance"])

            if distance < 0:
                raise ValueError("Road distances cannot be negative.")

            graph.setdefault(source, [])
            graph.setdefault(destination, [])

            graph[source].append((destination, distance))
            graph[destination].append((source, distance))

    return graph


#Dijkstra's shortest-path algorithm
def dijkstra(graph, start):
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}

    if start not in graph:
        raise ValueError(f"Unknown starting point: {start}")

    distances[start] = 0
    queue = [(0, start)]

    while queue:
        distance, node = heapq.heappop(queue)

        if distance != distances[node]:
            continue

        for neighbour, weight in graph[node]:
            new_distance = distance + weight

            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                previous[neighbour] = node
                heapq.heappush(
                    queue, (new_distance, neighbour)
                )

    return distances, previous


def get_path(previous, target):
    path = []
    node = target

    while node is not None:
        path.append(node)
        node = previous[node]

    return path[::-1]


#Display the complete weighted road graph
def print_graph(graph):
    print("\n--- PHASE 3: ROAD GRAPH ---")

    for location in sorted(graph):
        neighbours = sorted(graph[location])

        connections = ", ".join(
            f"{neighbour} ({distance:g} km)"
            for neighbour, distance in neighbours
        )

        print(f"{location} -> {connections}")


#Find and display shortest paths from depot
def print_shortest_paths(graph, depot, destinations):
    print("\n--- PHASE 3: DIJKSTRA SHORTEST PATHS ---")

    distances, previous = dijkstra(graph, depot)

    for destination in sorted(set(destinations)):
        if destination not in graph:
            print(f"{depot} -> {destination}: Unknown location")
            continue

        if distances[destination] == float("inf"):
            print(f"{depot} -> {destination}: Unreachable")
            continue

        path = get_path(previous, destination)

        print(f"\nDestination: {destination}")
        print("Shortest path:", " -> ".join(path))
        print("Shortest distance:",
              round(distances[destination], 2), "km")


#Visualize the weighted road graph
def plot_graph(graph, filename="images/road_graph.png"):
    if not graph:
        print("Cannot plot an empty road graph.")
        return

    nodes = sorted(graph)
    total_nodes = len(nodes)

    # Arrange locations in a circle
    positions = {}

    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / total_nodes

        positions[node] = (
            math.cos(angle),
            math.sin(angle)
        )

    plt.figure(figsize=(10, 8))

# Draw each undirected road only once
    drawn_edges = set()

    for source in nodes:
        for destination, distance in graph[source]:
            edge = tuple(sorted((source, destination)))

            if edge in drawn_edges:
                continue

            drawn_edges.add(edge)

            x1, y1 = positions[source]
            x2, y2 = positions[destination]

            plt.plot(
                [x1, x2],
                [y1, y2],
                color="gray",
                linewidth=1.5,
                zorder=1
            )

            # Display road distance near the midpoint
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2

            plt.text(
                mid_x,
                mid_y,
                f"{distance:g} km",
                fontsize=8,
                ha="center",
                va="center",
                bbox=dict(facecolor="white", alpha=0.8)
            )

    # Draw location nodes and labels
    for node, (x, y) in positions.items():
        plt.scatter(
            x, y,
            s=800,
            color="skyblue",
            edgecolors="black",
            zorder=2
        )

        plt.text(
            x, y,
            node,
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=3
        )

    plt.title("Mini-Courier Planner: Weighted Road Graph")
    plt.axis("off")
    plt.tight_layout()

    # Create the images directory if needed
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    # Save the graph for the project report
    plt.savefig(filename, dpi=300, bbox_inches="tight")

    print(f"\nRoad graph image saved to: {filename}")

    plt.show()
    plt.close()

