from search import Problem, Node, SimpleProblemSolvingAgentProgram, uniform_cost_search, recursive_best_first_search, depth_first_tree_search
from utils import distance

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
        return [pos for pos in [right,up,left,down] if self.__valid_pos(pos)]

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
def print_matrix(m):
    height = len(m)
    width = len(m[0])
    for i in range(height):
        print("[", end = '')
        for j in range(width):
            print(m[i][j], end = ',')
        print("],")

start = tuple((9, 2))
goal  = tuple((2, 11))

small_map = [
    [1,1,1,1,1,1,1],
    [1,0,0,0,1,0,1],
    [1,0,0,0,1,0,1],
    [1,0,1,0,1,0,1],
    [1,0,1,0,0,0,1],
    [1,0,1,0,0,0,1],
    [1,1,1,1,1,1,1],
]
# small_map[start[0]][start[1]] = START
# small_map[goal[0]][goal[1]] = GOAL

medium_map = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,1,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,1,0,0,0,0,1],
	[1,0,0,0,0,1,0,0,1,0,0,0,0,1],
	[1,0,0,0,0,1,0,0,0,0,0,0,0,1],
	[1,0,0,0,0,1,0,0,0,0,0,0,0,1],
	[1,0,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
medium_map[start[0]][start[1]] = START
medium_map[goal[0]][goal[1]] = GOAL


print_matrix(medium_map)

problem = PathfindingRobotProblem(start, medium_map)
print("The search found the following solution: ")
seq = uniform_cost_search(problem).solution()
print(seq)

for i, j in seq[:-1]:
    medium_map[i][j] = '*'

print_matrix(medium_map)
