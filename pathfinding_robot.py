from search import Problem
from utils import distance

infinity = float('inf')

EMPTY = 0
WALL  = 1
START = 2
GOAL  = 3

class PathfindingRobotProblem(Problem):
    
    """The problem of finding a path in a labyrinth defined by a grid map (i.e. an n x m matrix)."""

    """Parameters
    initial : (int, int)
      inverse ordered pair with the initial coordinate at the map, i.e. (y0,x0)
    goal : (int, int)
      inverse ordered pair with the goal coordinate at the map, i.e. (Y,X)
    map : [[int]]
      matrix representing the labyrinth's map, where the cell's values represent:
        0 - empty cell
        1 - wall
        2 - robot's initial (start) position
        3 - robot's target (goal) position
      obs.: map is a list of rows: line i, row j <-> map[i][j]
            therefore the cartesian coordinate (x,y) maps to map[y][x]
    """
    def __init__(self, initial, goal, map):
        Problem.__init__(self, initial, goal)
        self.map = map
        self.height = len(map) # number of rows
        self.width = len(map[0]) # number of columns

    """Parameters
    y : int
      y (vertical) coordinate at the map
    x : int
      x (horizontal) coordinate at the map
    obs.: coord(x, y) <-> map[y][x]
    """
    def __valid_pos(self, y, x):
        return y in range(0, self.height) and x in range(0, self.width) and self.map[y][x] != WALL

    """Parameters
    state : (int, int)
      inverse ordered pair with the robot's current coordinate at the map, i.e. (y,x)
    """
    def actions(self, state):
        actions = list() # []
        y, x = state

        if self.__valid_pos(y, x-1):
            actions.append(tuple((y, x-1))) # left
        
        if self.__valid_pos(y, x+1):
            actions.append(tuple((y, x+1))) # right
        
        if self.__valid_pos(y-1, x):
            actions.append(tuple((y-1, x))) # up
        
        if self.__valid_pos(y+1, x):
            actions.append(tuple((y+1, x))) # down

        return actions

    """Parameters
    state : (int, int)
      inverse ordered pair with the robot's current coordinate at the map, i.e. (y,x)
    action : (int, int)
      inverse ordered pair with the neighbouring position the robot will move to, i.e. (y',x')
    """
    def result(self, state, action):
        return action

    """Parameters
    cost_so_far : int
      cost already paid to get to state A
    A : (int, int)
      inverse ordered pair with the robot's current position, i.e. (y,x)
    action : (int, int)
      inverse ordered pair with the neighbouring position the robot would move to, i.e. (y',x')
    B : (int, int)
      inverse ordered pair with the robot's next position, i.e. (y',x')
    """
    def path_cost(self, cost_so_far, A, action, B):
        """If the move is valid (i.e. A and B are neighbors, and the action takes to B) it's cost is 1."""
        y1, x1 = A
        y2, x2 = B
        if action == B and abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
          return cost_so_far + 1 if self.__valid_pos(y2, x2) else infinity
        else:
          return infinity
