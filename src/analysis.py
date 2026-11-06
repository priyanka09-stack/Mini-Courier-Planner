"""
Phase 4 extras: correctness tests, algorithm comparisons, large benchmark,
route visualization.  Run from project root:  python -m src.analysis
"""
import csv, itertools, math, os, random, statistics, time
import matplotlib.pyplot as plt

from src.sorting import sort_parcels
from src.knapsack import knapsack
from src.dijkstra import load_graph, dijkstra
from src.tsp import delivery_route
from src.performance import generate_parcels

os.makedirs("images", exist_ok=True)


def load_parcels(filename="datasets/parcels.csv"):
    with open(filename, newline="") as f:
        return [{"id": r["parcel_id"], "destination": r["destination"],
                 "weight": int(r["weight"]), "value": int(r["value"]),
                 "priority": int(r["priority"]), "deadline": r["deadline"]}
                for r in csv.DictReader(f)]


def ms(fn, *args):
    """Run fn(*args), return (time in milliseconds, result)."""
    t = time.perf_counter()
    out = fn(*args)
    return (time.perf_counter() - t) * 1000, out

# ---------- alternatives used for comparison ----------
def bubble_sort_parcels(parcels):
    a = parcels[:]
    key = lambda p: (-p["priority"], p["deadline"], -(p["value"] / p["weight"]))
    for i in range(len(a)):
        for j in range(len(a) - i - 1):
            if key(a[j]) > key(a[j + 1]):
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def greedy_knapsack(parcels, capacity):
    chosen, w, v = [], 0, 0
    for p in sorted(parcels, key=lambda p: -p["value"] / p["weight"]):
        if w + p["weight"] <= capacity:
            chosen.append(p); w += p["weight"]; v += p["value"]
    return chosen, v


def brute_force_tsp(graph, depot, stops):
    dist = {s: dijkstra(graph, s)[0] for s in [depot] + list(stops)}
    best = (float("inf"), None)
    for perm in itertools.permutations(stops):
        order = [depot, *perm, depot]
        d = sum(dist[a][b] for a, b in zip(order, order[1:]))
        best = min(best, (d, order))
    return best




# ---------- 1. correctness tests ----------
def run_tests():
    parcels, graph = load_parcels(), load_graph("datasets/roads.csv")
    key = lambda p: (-p["priority"], p["deadline"], -(p["value"] / p["weight"]))
    assert sort_parcels(parcels) == sorted(parcels, key=key)
    print("PASS  merge sort matches Python sorted() on sample data")

    sel, val, _ = knapsack(parcels, 15)
    best = max(sum(p["value"] for p in c)
               for r in range(len(parcels) + 1)
               for c in itertools.combinations(parcels, r)
               if sum(p["weight"] for p in c) <= 15)
    assert val == best == 325
    print(f"PASS  knapsack value {val} equals brute-force optimum {best}")

    nodes = list(graph)
    fw = {a: {b: (0 if a == b else float("inf")) for b in nodes} for a in nodes}
    for a in graph:
        for b, w in graph[a]:
            fw[a][b] = min(fw[a][b], w)
    for k in nodes:
        for i in nodes:
            for j in nodes:
                fw[i][j] = min(fw[i][j], fw[i][k] + fw[k][j])
    for a in nodes:
        d, _ = dijkstra(graph, a)
        assert all(abs(d[b] - fw[a][b]) < 1e-9 for b in nodes)
    print("PASS  Dijkstra distances match Floyd-Warshall for every source node")

    _, dist, order = delivery_route(graph, "D0", ["A", "B", "C"])
    assert dist == 18.0
    print("PASS  nearest-neighbour route D0->C->A->B->D0 = 18 km")


# ---------- 2. algorithm comparisons ----------
def run_comparisons():
    parcels, graph = load_parcels(), load_graph("datasets/roads.csv")
    sort_key = lambda p: (-p["priority"], p["deadline"], -(p["value"] / p["weight"]))

    print("\nSORTING (ms)      n   merge   bubble  built-in")
    for n in (100, 500, 1000):
        data = generate_parcels(n)
        m, _ = ms(sort_parcels, data)
        b, _ = ms(bubble_sort_parcels, data)
        s, _ = ms(lambda d: sorted(d, key=sort_key), data)
        print(f"             {n:6d} {m:7.2f} {b:8.2f} {s:8.2f}")

    print("\nKNAPSACK: DP vs greedy (value/weight ratio)")
    _, gv = greedy_knapsack(parcels, 15)
    print(f"  sample data, capacity 15 : DP = 325, greedy = {gv}")
    wins = 0
    for seed in range(200):
        ps = generate_parcels(15, seed)
        dp_v = knapsack(ps, 25)[1]
        gr_v = greedy_knapsack(ps, 25)[1]
        wins += dp_v > gr_v
    print(f"  200 random sets (15 parcels, cap 25): DP strictly better in {wins}")

    print("\nTSP: nearest neighbour vs brute force")
    for label, stops in (("3 stops (A,B,C)", ["A", "B", "C"]),
                         ("6 stops (A-F)", ["A", "B", "C", "D", "E", "F"])):
        _, nn, order = delivery_route(graph, "D0", stops)
        t, (bf, bf_order) = ms(brute_force_tsp, graph, "D0", stops)
        print(f"  {label}: NN = {nn:g} km, optimal = {bf:g} km "
              f"({(nn / bf - 1) * 100:.1f}% longer), brute force took {t:.2f} ms")

# ---------- 3. large benchmark ----------
def sparse_graph(n, seed=1):
    """Random connected graph: a random tree + 2n extra random roads."""
    rng = random.Random(seed)
    nodes = ["D0"] + [f"N{i}" for i in range(1, n + 1)]
    g = {v: [] for v in nodes}

    def add(a, b):
        w = rng.randint(1, 20)
        g[a].append((b, w))
        g[b].append((a, w))

    for i in range(1, len(nodes)):          # tree => graph is connected
        add(nodes[i], nodes[rng.randrange(i)])
    for _ in range(2 * n):                  # extra roads
        a, b = rng.sample(nodes, 2)
        add(a, b)
    return g


def run_large_benchmark():
    rows = []
    for n in (100, 200, 500, 1000):
        parcels, g = generate_parcels(n), sparse_graph(n)
        cap = n * 3
        stops = [f"N{i}" for i in range(1, n + 1)]
        rows.append({"n": n,
                     "sort_ms": ms(sort_parcels, parcels)[0],
                     "knapsack_ms": ms(knapsack, parcels, cap)[0],
                     "dijkstra_ms": ms(dijkstra, g, "D0")[0],
                     "routing_ms": ms(delivery_route, g, "D0", stops)[0]})
        print({k: round(v, 2) for k, v in rows[-1].items()})

    with open("images/runtime_large.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    plt.figure(figsize=(9, 5))
    for col in ("sort_ms", "knapsack_ms", "dijkstra_ms", "routing_ms"):
        plt.plot([r["n"] for r in rows], [r[col] for r in rows],
                 marker="o", label=col.replace("_ms", ""))
    plt.yscale("log")
    plt.xlabel("Input size n")
    plt.ylabel("Time (ms, log scale)")
    plt.title("Runtime on larger inputs (sparse random graph)")
    plt.legend()
    plt.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig("images/runtime_large.png", dpi=200)
    plt.close()

# ---------- 4. route visualization ----------
def plot_route(graph, route, filename="images/route_map.png"):
    nodes = sorted(graph)
    pos = {n: (math.cos(2 * math.pi * i / len(nodes)),
               math.sin(2 * math.pi * i / len(nodes)))
           for i, n in enumerate(nodes)}

    plt.figure(figsize=(8, 7))
    for a in graph:                          # all roads in light gray
        for b, _ in graph[a]:
            plt.plot(*zip(pos[a], pos[b]), color="lightgray", zorder=1)
    for a, b in zip(route, route[1:]):       # route in red arrows
        plt.annotate("", xy=pos[b], xytext=pos[a], zorder=3,
                     arrowprops=dict(arrowstyle="->", color="red", lw=2,
                                     shrinkA=18, shrinkB=18))
    for n, (x, y) in pos.items():            # nodes (depot in gold)
        plt.scatter(x, y, s=700, color="gold" if n == "D0" else "skyblue",
                    edgecolors="black", zorder=2)
        plt.text(x, y, n, ha="center", va="center",
                 fontweight="bold", zorder=4)

    plt.title("Final delivery route: " + " -> ".join(route))
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()
    print("route image saved to", filename)

if __name__ == "__main__":
    print("=== CORRECTNESS TESTS ===")
    run_tests()
    print("\n=== ALGORITHM COMPARISONS ===")
    run_comparisons()
    print("\n=== LARGE BENCHMARK ===")
    run_large_benchmark()
    g = load_graph("datasets/roads.csv")
    plot_route(g, delivery_route(g, "D0", ["A", "B", "C"])[0])