
# 2. Merge Sort: Sort parcels by priority and deadline
def sort_parcels(parcels):
    def key(p):
        return (
            -p["priority"],
            p["deadline"],
            -(p["value"] / p["weight"])
        )

    if len(parcels) <= 1:
        return parcels[:]

    mid = len(parcels) // 2
    left = sort_parcels(parcels[:mid])
    right = sort_parcels(parcels[mid:])

    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result
