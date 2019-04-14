from pathfinding_robot import *

euclidean_heuristic = lambda node, goal=goal: euclidean(node, goal) # diagonal moves cost sqrt(2)
manhattan_heuristic = lambda node, goal=goal: manhattan(node, goal) # diagonal moves cost 2
diagonal_heuristic  = lambda node, goal=goal: diagonal(node, goal)  # diagonal moves cost 1

search_methods = {
    "depth_first_search" : 
        (depth_first_graph_search, depth_first_search_for_vis),
    "breadth_first_search" : 
        (breadth_first_graph_search, breadth_first_search_for_vis),
    "astar_search" : 
        (astar_search, astar_search_for_vis),
    "best_first_search-manhattan" : 
        (lambda problem: best_first_graph_search(problem, manhattan_heuristic), 
         lambda problem: best_first_search_for_vis(problem, manhattan_heuristic)),
    "best_first_search-euclidean" : 
        (lambda problem: best_first_graph_search(problem, euclidean_heuristic), 
         lambda problem: best_first_search_for_vis(problem, euclidean_heuristic)),
    "best_first_search-diagonal" : 
        (lambda problem: best_first_graph_search(problem, diagonal_heuristic), 
         lambda problem: best_first_search_for_vis(problem, diagonal_heuristic)),
}

maze  = big_maze
start = maze.start
goal  = maze.goal
maze.map[start[0]][start[1]] = START
maze.map[goal[0]][goal[1]] = GOAL

# Problem set up
problem = PathfindingRobotProblem(start, goal, maze.map)

for method_name, method in search_methods.items():    
    start_time = time()
    method[0](problem)
    end_time = time()

    node, reached = method[1](problem)
    seq = node.solution()
    
    save_heatmap(start, goal, maze.map, reached, seq, f'./heatmaps/{method_name}.png')
    
    file_name = 'methods.data'
    f = open(file_name, 'a+')
    f.write('{}\n -{:.2f}ms\n -{} reached nodes\n -{} steps in solution\n'.format(method_name, 
        (end_time - start_time)*1000, len(reached), len(seq)))
    f.close()