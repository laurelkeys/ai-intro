from search import Node, PriorityQueue, memoize, deque

"""Methods from search.py altered to return the list of reached nodes for visualization"""

failure = Node('failure', path_cost=float('inf')) # Indicates an algorithm couldn't find a solution.

# ______________________________________________________________________________
# Uninformed search algorithms

def depth_first_search_for_vis(problem):
    frontier = [(Node(problem.initial))]  # Stack
    explored = set()
    reached = []
    while frontier:
        node = frontier.pop()
        reached.append(node.state)
        if problem.goal_test(node.state):
            return (node, reached)
        explored.add(node.state)
        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored and
                        child not in frontier)
    return (failure, reached)

def breadth_first_search_for_vis(problem):
    node = Node(problem.initial)
    reached = []
    reached.append(node.state)
    if problem.goal_test(node.state):
        return (node, reached)
    frontier = deque([node])
    explored = set()
    while frontier:
        node = frontier.popleft()
        explored.add(node.state)
        reached.append(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                if problem.goal_test(child.state):
                    return (child, reached)
                frontier.append(child)
    return (failure, reached)

def uniform_cost_search_for_vis(problem):
    return best_first_search_for_vis(problem, lambda node: node.path_cost)

# ______________________________________________________________________________
# Informed (heuristic) search algorithms

def best_first_search_for_vis(problem, f):
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = set()
    reached = []
    while frontier:
        node = frontier.pop()
        reached.append(node.state)
        if problem.goal_test(node.state):
            return (node, reached)
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return (failure, reached)

def astar_search_for_vis(problem, h=None):
    h = memoize(h or problem.h, 'h')
    return best_first_search_for_vis(problem, lambda n: n.path_cost + h(n))

# TODO compare BFS and A* when passing manhattan as the heuristic
