# TODO minimize imports
from search import *
from pathfinding_robot_maps import * 
from pathfinding_robot_heuristics import *
from utils import distance
from random import shuffle
import matplotlib.pyplot as plt

infinity = float('inf')

EMPTY = 0
WALL  = 1
START = 2
GOAL  = 3

index_by = lambda ij_tuple, m: m[ij_tuple[0]][ij_tuple[1]]

# ______________________________________________________________________________
class PathfindingRobotProblem(Problem):
    
    """The problem of finding a path in a labyrinth defined by a grid map (i.e. an n x m matrix)."""

    """
    Parameters
      initial : (int, int)
        robot's initial postition at the map, i.e. (i0,j0)
      goal : (int, int)
        goal postition at the map, i.e. (I,J)
      map : [[int]]
        matrix representing the labyrinth's map, where the cell's values represent:
          0 - empty cell
          1 - wall
          2 - robot's initial (start) position
          3 - robot's target (goal) position
        obs.: map is a list of rows: line i, row j <-> map[i][j]
    """
    def __init__(self, initial, goal, map):
        assert(index_by(initial, map) == START)
        assert(index_by(goal, map) == GOAL)

        self.map    = map
        self.height = len(map) # number of rows (m)
        self.width  = len(map[0]) # number of columns (n)

        self.initial = initial
        self.goal    = goal
        
        # self.directions = [(-1, -1), (-1,  0), (-1,  1),
        #                    ( 0, -1),           ( 0,  1),
        #                    ( 1, -1), ( 1,  0), ( 1,  1)]
        self.directions = [          (-1,  0), 
                           ( 0, -1),           ( 0,  1),
                                     ( 1,  0),         ]
        
        Problem.__init__(self, self.initial, self.goal)

    """
    Parameters
      pos : (int, int)
        (i, j) postition at the map
    """
    def __valid_pos(self, pos):
        i, j = pos
        return i in range(0, self.height) and j in range(0, self.width) and self.map[i][j] != WALL

    """
    Parameters
      pos1 : (int, int)
        (i, j) postition at the map
      pos2 : (int, int)
        (i', j') postition at the map
    """
    def __valid_move(self, pos1, pos2):
        di, dj = [abs(k1 - k2) for (k1, k2) in zip(pos1, pos2)]
        return self.__valid_pos(pos1) and di + dj <= 1 and self.__valid_pos(pos2) # TODO change to 2 if diagonal moves are allowed

    """
    Parameters
      state : (int, int)
        robot's current postition at the map, i.e. (i,j)
    """
    def actions(self, state):
        i, j = state
        actions_list = [(i + di, j + dj) for (di, dj) in self.directions]
        # shuffle(actions_list) # randomizes actions' order
        return [pos for pos in actions_list if self.__valid_move(state, pos)]

    """
    Parameters
      state : (int, int)
        robot's current postition at the map, i.e. (i,j)
      action : (int, int)
        (neighbouring) position the robot would move to, i.e. (i',j')
    """
    def result(self, state, action):
        return action # assumed to be a valid action in the state

    """
    Parameters
      state : (int, int)
        robot's current postition at the map, i.e. (i,j)
    """
    def goal_test(self, state):
        return state == self.goal

    """
    Parameters
      cost_so_far : int
        cost already paid to get to state A
      A : (int, int)
        robot's current postition at the map, i.e. (i,j)
      action : (int, int)
        neighbouring position the robot would move to, i.e. (i',j')
      B : (int, int)
        robot's next postition at the map, i.e. (i',j')
    """
    def path_cost(self, cost_so_far, A, action, B):
        """If the move is valid (i.e. A and B are neighbors, and the action takes to B) it's cost is 1."""
        if action == B and self.__valid_move(A, B):
            return cost_so_far + 1 # if di + dj <= 1 else 2**0.5 # TODO change if diagonal moves are allowed but more costly
        else:
            return infinity

# ______________________________________________________________________________
def best_first_search_for_vis(problem, f):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node.depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned."""
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    global exploredd
    exploredd = []
    explored = set()
    while frontier:
        node = frontier.pop()
        exploredd.append(node.state)
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return None

# ______________________________________________________________________________
start = tuple((5, 1))
goal  = tuple((1, 5))

small_map[start[0]][start[1]] = START
small_map[goal[0]][goal[1]] = GOAL

# print_matrix(small_map)
problem = PathfindingRobotProblem(start, goal, small_map)
print("The search found the following solution: ")

heuristic = lambda node, goal=goal: euclidean(node, goal)
seq = best_first_search_for_vis(problem, heuristic).solution()

# print(seq)
plt.matshow(small_map, fignum=0)
plt.show(block=False)
plt.pause(.05)
small_map[start[0]][start[1]] = 16
small_map[goal[0]][goal[1]] = 16
for node in exploredd:
    i, j = node
    if node != start and node != goal:
        small_map[i][j] = 6
        plt.matshow(small_map, fignum=0)
        plt.pause(.05)
for i, j in seq[:-1]:
    small_map[i][j] = 8
    plt.matshow(small_map, fignum=0)
    plt.pause(.05)
plt.show()


# plt.matshow(m, fignum=0)
# plt.show(block=False)
# plt.pause(.1)
# m[0][0] = -10000
# plt.matshow(m, fignum=0)
# plt.pause(.3)
# m[0][0] = 10000
# plt.matshow(m, fignum=0)
# plt.show()

# print_matrix(small_map)

"""
uninformed searches:
    searches that work:
        depth_first_graph_search
        breadth_first_graph_search
    searches that do not work:
        loop:
            breadth_first_tree_search
            depth_first_tree_search
        FIXME:
            depth_limited_search (obs.: define limit)
            iterative_deepening_search
informed searches:
    searches that work:
        best_first_graph_search (obs.: define f)
        uniform_cost_search
    TODO:
        astar_search (obs.: define h)
        greedy_best_first_graph_search (obs.: best_first_graph_search with f = h)
        recursive_best_first_search (obs.: define h)
"""

