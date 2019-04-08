from search import Node, PriorityQueue, memoize, deque

# ______________________________________________________________________________
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
    return (None, reached)

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
    return (None, reached)

def breadth_first_graph_search(problem):
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
    return (None, reached)
