def euclidian(node, goal):
    i, j = node.state
    I, J = goal
    return (abs(i - I)**2 + abs(j - J)**2)**0.5

def manhattan(node, goal):
    i, j = node.state
    I, J = goal
    return abs(i - I) + abs(j - J)
