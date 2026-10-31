def knapsack(parcels, capacity):                         # Dynamic Programming: 0/1 Knapsack
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        weight = parcels[i - 1]["weight"]
        value = parcels[i - 1]["value"]

        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]

            if weight <= w:
                dp[i][w] = max(
                    dp[i][w],
                    dp[i - 1][w - weight] + value
                )

    selected = []
    w = capacity

    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(parcels[i - 1])
            w -= parcels[i - 1]["weight"]

    selected.reverse()
    return selected, dp[n][capacity] ,dp

