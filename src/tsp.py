from src.dijkstra import dijkstra, get_path


# 3. Nearest Neighbour TSP approximation
def delivery_route(graph, depot, destinations):
    if depot not in graph:
        raise ValueError(f"Unknown depot: {depot}")

    remaining = set(destinations)
    remaining.discard(depot)

    unknown = remaining - set(graph)

    if unknown:
        raise ValueError(
            f"Unknown destinations: {sorted(unknown)}"
        )

    current = depot
    route = [depot]
    visit_order = [depot]
    total_distance = 0.0

    while remaining:
        distances, previous = dijkstra(graph, current)

        reachable = [
            node for node in remaining
            if distances[node] != float("inf")
        ]

        if not reachable:
            raise ValueError(
                f"Unreachable destinations: {sorted(remaining)}"
            )

        # Select the nearest unvisited destination
        next_stop = min(
            reachable,
            key=lambda node: (distances[node], node)
        )

        # Reconstruct the shortest road path
        path = get_path(previous, next_stop)

        total_distance += distances[next_stop]
        route.extend(path[1:])

        remaining.remove(next_stop)
        current = next_stop
        visit_order.append(next_stop)

    # Return to depot after visiting all destinations
    if current != depot:
        distances, previous = dijkstra(graph, current)

        if distances[depot] == float("inf"):
            raise ValueError("Cannot return to depot.")

        path = get_path(previous, depot)

        total_distance += distances[depot]
        route.extend(path[1:])
        visit_order.append(depot)

    return route, total_distance, visit_order
