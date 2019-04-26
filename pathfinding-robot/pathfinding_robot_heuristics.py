# Euclidean distance (diagonal moves cost sqrt(2))
def euclidean(node, goal):
    di, dj = [abs(k1 - k2) for (k1, k2) in zip(node.state, goal)]
    return (di**2 + dj**2)**0.5

# Manhattan distance (diagonal moves cost 2)
def manhattan(node, goal):
    di, dj = [abs(k1 - k2) for (k1, k2) in zip(node.state, goal)]
    return di + dj

# Chebyshev distance (diagonal moves cost 1)
def diagonal(node, goal):
    di, dj = [abs(k1 - k2) for (k1, k2) in zip(node.state, goal)]
    return max(di, dj) # chebyshev distance

# Path cost
def g(node, goal):
    return node.path_cost
