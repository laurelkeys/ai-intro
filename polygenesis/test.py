import os
from sys import argv
from Runner import Runner
from utils import WHITE, FitnessCalculator

try:
    image_path = argv[1]
    image_name = os.path.splitext(os.path.split(image_path)[-1])[0]
    polygon_count = int(argv[2])
    vertices_count = 3 if len(argv) <= 3 else int(argv[3])
    assert(vertices_count >= 3 and vertices_count <= 255)
    if polygon_count != 64:
        print(f"WARNING! polygon_count = {polygon_count} (default is 64)")
    if vertices_count != 3:
        print(f"WARNING! vertices_count = {vertices_count} (default is 3)")
except:
    print("usage: python run.py image_path polygon_count [vertices_count]")
    exit()

# ______________________________________________________________________________

def print_run():
    stopping_criteria = ""
    if max_unimproved_cycles != None: stopping_criteria += f"\n    max_unimproved_cycles = {max_unimproved_cycles}"
    if fitness_limit != None: stopping_criteria += f"\n    fitness_limit         = {fitness_limit}"
    if duration_limit != None: stopping_criteria += f"\n    duration_limit        = {duration_limit}"

    print(f"""
Running with:
    image_path     = {image_path}
    polygon_count  = {polygon_count}
    vertices_count = {vertices_count}

    population_size     = {population_size}
    mutation_rate       = {mutation_rate}
    crossover_rate      = {crossover_rate}
    selection_strategy  = {selection_strategy}
    crossover_strategy  = {crossover_strategy}
    substitution_method = {substitution_method}

    fitness_func                = {fitness_func.__name__}
    hard_mutation_fitness_limit = {hard_mutation_fitness_limit:_d}
    {stopping_criteria}
""")

# ______________________________________________________________________________

save_path   = os.path.join("tests", image_name)
print_cycle = 100
save_cycle  = 500

# NOTE set values
population_size     = 8
mutation_rate       = 1.0
crossover_rate      = 0.63
selection_strategy  = 'stochastic_acceptance'  # 'first_packs', 'truncation', 'stochastic_acceptance', 'roulette_wheel'
crossover_strategy  = 'uniform'                # 'single_point', 'single_point_stochastic', 'uniform'
substitution_method = 'plus_selection'         # 'plus_selection', 'comma_selection', 'tournament'

runner = Runner(
    image_path, polygon_count, vertices_count,
    population_size=population_size,
    max_internal_size=(200, 200),
    print_cycle=print_cycle
)

# NOTE set values
fitness_func                = FitnessCalculator(runner.image).ssd
hard_mutation_fitness_limit = 150_000_000 # TODO change based on fitness_func

# NOTE set values
max_unimproved_cycles = None
fitness_limit         = None
duration_limit        = None

print_run()

# ______________________________________________________________________________

(runner
    .save_dna_to(os.path.join(save_path, "dna"))
    .save_best_to(save_path, save_cycle)
    .save_all_to(save_path, save_cycle)
	
	.plot_at(plot_cycle=10, plot_time_on_x=False, show_plot=False, 
	         save_plot=True, save_path=os.path.join(save_path, "plot"))
    
    # .set_bg_color(WHITE) # TODO uncomment for Stormtrooper
	
	.set_fitness_func(fitness_func)
    .set_mutation_rate(mutation_rate)
    .set_crossover_rate(crossover_rate)
    .set_selection_strategy(selection_strategy)
    .set_crossover_strategy(crossover_strategy)
    .set_substitution_method(substitution_method)
    
	.set_mutation_params(hard_mutation_fitness_limit, random_hard_mutation_prob=0.005)
    
	.halt_on(max_unimproved_cycles, fitness_limit, duration_limit)

).run(use_image_colors=True)