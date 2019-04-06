def euclidean(node, goal):
    i, j = node.state
    I, J = goal
    return (abs(i - I)**2 + abs(j - J)**2)**0.5

def manhattan(node, goal):
    i, j = node.state
    I, J = goal
    return abs(i - I) + abs(j - J)

def sqrt_manhattan(node, goal):
    i, j = node.state
    I, J = goal
    return (abs(i - I) + abs(j - J))**0.5

def diagonal(node, goal):
    i, j = node.state
    I, J = goal
    di = abs(i - I)
    dj = abs(j - J)
    return (di + dj) - min(di, dj) # diagonal moves cost 1

def octile(node, goal):
    i, j = node.state
    I, J = goal
    di = abs(i - I)
    dj = abs(j - J)
    return (di + dj) - (2**0.5 - 2) * min(di, dj) # diagonal moves cost sqrt(2)


def g(node, goal):
    return node.path_cost

def h(node, goal):
    return euclidean(node, goal)

def f(node, goal):
    return g(node, goal) + h(node, goal)
