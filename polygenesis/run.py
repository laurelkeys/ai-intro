import os
from sys import argv
from Runner import Runner
from utils import WHITE, BLACK, FitnessCalculator

try:
    image_path = argv[1]
    polygon_count = int(argv[2])
    vertices_count = 3 if len(argv) <= 3 else int(argv[3])
    max_cycles = -1 if len(argv) <= 4 else int(argv[4])
    assert(polygon_count >= 0 and polygon_count <= 255)
    assert(vertices_count >= 3 and vertices_count <= 255)
except:
    print("usage: python run.py image_path polygon_count [vertices_count] [max_cycles]")
    exit()

runner = Runner(
    image_path, polygon_count, vertices_count,
    population_size=2,
    max_internal_size=(200, 200),
    print_cycle=500
)

# NOTE these paths consider that you're running on the same directory as this file
#      also, the min_fitness value to save the DNA should be changed depending on the fitness function

(runner
    .save_dna_to(save_path=os.path.join("generated", "dna"), min_fitness=100_000_000)
    .save_best_to(save_path="generated", save_cycle=4_000)
    # .save_all_to(save_path="generated", save_cycle=10_000)
    # .save_plot_to(save_path=os.path.join("generated", "plot"))
    # .show_at(show_cycle=1, show_all=True)
    .plot_at(plot_cycle=1, plot_time_on_x=False, show_plot=True, save_plot=True, save_path=os.path.join("generated", "plot"))
    .set_fitness_func(FitnessCalculator(runner.image).ssd,
                      partial_fitness_func=FitnessCalculator(runner.image).partial_ssd)
    # .set_bg_color(WHITE)
    .set_mutation_rate(0.1)
    .set_crossover_rate(1.0)
    .set_selection_strategy('truncation') # 'first_packs', 'truncation', 'stochastic_acceptance', 'roulette_wheel'
    .set_crossover_strategy('single_point') # 'single_point', 'single_point_stochastic', 'uniform'
    .set_substitution_method('plus_selection') # 'plus_selection', 'comma_selection', 'tournament'
    .set_mutation_params(hard_mutation_fitness_limit=150_000_000, random_hard_mutation_prob=0.005)
    # .set_max_unimproved_cycles(1000)

).run(use_partial_fitness=False, use_image_colors=True)