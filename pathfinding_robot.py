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

# ______________________________________________________________________________
class PathfindingRobotProblem(Problem):
    
    """The problem of finding a path in a labyrinth defined by a grid map (i.e. an n x m matrix)."""

    """Parameters
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
    def __init__(self, initial, map):
        self.map = map
        self.height = len(map) # number of rows
        self.width = len(map[0]) # number of columns
        self.initial = initial
        Problem.__init__(self, self.initial)

    """Parameters
    pos : (int, int)
      (i, j) postition at the map
    """
    def __valid_pos(self, pos):
        i, j = pos
        return i in range(0, self.height) and j in range(0, self.width) and self.map[i][j] != WALL

    """Parameters
    state : (int, int)
      robot's current postition at the map, i.e. (i,j)
    """
    def actions(self, state):
        i, j  = state
        left  = tuple((i, j - 1))
        right = tuple((i, j + 1))
        up    = tuple((i - 1, j))
        down  = tuple((i + 1, j))
        actions_list = [right,up,left,down]
        shuffle(actions_list) # randomizes actions' order
        return [pos for pos in actions_list if self.__valid_pos(pos)]

    """Parameters
    state : (int, int)
      robot's current postition at the map, i.e. (i,j)
    action : (int, int)
      (neighbouring) position the robot would move to, i.e. (i',j')
    """
    def result(self, state, action):
        # FIXME make sure the action is valid
        return action

    """Parameters
    state : (int, int)
      robot's current postition at the map, i.e. (i,j)
    """
    def goal_test(self, state):
        i, j = state
        return self.map[i][j] == GOAL

    """Parameters
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
        i1, j1 = A
        i2, j2 = B
        if action == B and abs(i1 - i2) <= 1 and abs(j1 - j2) <= 1:
            return cost_so_far + 1 if self.__valid_pos(B) else infinity
        else:
            return infinity

# ______________________________________________________________________________
start = tuple((50, 10))
goal  = tuple((10, 50))

big_map[start[0]][start[1]] = START
big_map[goal[0]][goal[1]] = GOAL

# print_matrix(big_map)

problem = PathfindingRobotProblem(start, big_map)
print("The search found the following solution: ")
seq = best_first_graph_search(problem, f=lambda node, goal=goal: euclidian(node, goal)).solution()
# print(seq)

for i, j in seq[:-1]:
    big_map[i][j] = 8

print_matrix(big_map)

"""
uninformed searches:
    searches that work:
        depth_first_graph_search
        breadth_first_graph_search
        best_first_graph_search (obs.: define f)
        uniform_cost_search
    searches that do not work:
        loop:
            breadth_first_tree_search
            depth_first_tree_search
        FIXME:
            depth_limited_search (obs.: define limit)
            iterative_deepening_search
informed searches:
    TODO
"""
