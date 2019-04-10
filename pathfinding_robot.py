# TODO minimize imports

from pathfinding_robot_maps import *
from pathfinding_robot_searches import *
from pathfinding_robot_heuristics import *

# from search import *
from search import Problem, Node
from utils import distance

import numpy as np
from time import time
from random import shuffle
import matplotlib.pyplot as plt

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
    def __init__(self, initial, goal, map, diagonals_allowed=False, shuffle_actions_list=False):
        assert(index_by(initial, map) == START)
        assert(index_by(goal, map) == GOAL)

        self.map    = map
        self.height = len(map) # number of rows (m)
        self.width  = len(map[0]) # number of columns (n)

        self.initial = initial
        self.goal    = goal

        self.diagonals_allowed    = diagonals_allowed
        self.shuffle_actions_list = shuffle_actions_list
        
        if diagonals_allowed:
            self.directions = [(-1, -1), (-1,  0), (-1,  1),
                               ( 0, -1),           ( 0,  1),
                               ( 1, -1), ( 1,  0), ( 1,  1)]
        else:
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
        max_delta_sum = 1 if not self.diagonals_allowed else 2
        return self.__valid_pos(pos1) and di + dj <= max_delta_sum and self.__valid_pos(pos2)

    """
    Parameters
      state : (int, int)
        robot's current postition at the map, i.e. (i,j)
    """
    def actions(self, state):
        i, j = state
        actions_list = [(i + di, j + dj) for (di, dj) in self.directions]
        if (self.shuffle_actions_list):
            shuffle(actions_list) # randomizes actions' order
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
        # di, dj = [abs(k1 - k2) for (k1, k2) in zip(A, B)]
        if action == B and self.__valid_move(A, B):
            return cost_so_far + 1 # if di + dj <= 1 else 2**0.5 # TODO use this if diagonal moves are allowed but more costly
        else:
            return float('inf')
    
    """
    Parameters
      state : (int, int)
        robot's current postition at the map, i.e. (i,j), 
        for which we estimate the lowest path cost to the goal using an admissible heuristic
    """
    def h(self, state):
        if not self.diagonals_allowed:
            return manhattan(state, goal)
        else:
            return diagonal(state, goal) # TODO change to euclidean if diagonal moves cost more

# ______________________________________________________________________________

# Map set up
map = big_map
# start = (12, 2)
# goal  = (2, 12)
start = (50, 10)
goal  = (10, 50)

map[start[0]][start[1]] = START
map[goal[0]][goal[1]] = GOAL

# Problem set up
problem = PathfindingRobotProblem(start, goal, map)
heuristic = lambda node, goal=goal: manhattan(node, goal) + g(node, goal) # g(node, goal) + problem.h(node)

# Search execution
start_time = time()
node, reached = best_first_search_for_vis(problem, heuristic)
end_time = time()
seq = node.solution()

# Search display
ask_for_visualization = True

print( 'elapsed time:           {:.4f}ms'.format((end_time - start_time)*1000))
print(f'# of reached nodes:     {len(reached)}')
print(f'# of steps in solution: {len(seq)}')

if ask_for_visualization:
    visualize_solution(start, goal, map, reached, seq, False)
    reply = str(input('Show animation [Y/n]: ')).lower().strip()
    if reply[:1] not in ['n', 'N', 'no', 'No', 'NO']:
        plt.cla()
        visualize_solution(start, goal, map, reached, seq, True)
else:
    visualize_solution(start, goal, map, reached, seq, True)

