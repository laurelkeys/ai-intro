import os
from sys import argv
from Runner import Runner
from utils import WHITE, BLACK, FitnessCalculator

try:
    image_path = argv[1]
    image_name = os.path.splitext(os.path.split(image_path)[-1])[0]
    polygon_count = int(argv[2])
    vertices_count = 3 if len(argv) <= 3 else int(argv[3])
    assert(polygon_count >= 0 and polygon_count <= 255)
    assert(vertices_count >= 3 and vertices_count <= 255)
except:
    print("usage: python run.py image_path polygon_count [vertices_count]")
    exit()

runner = Runner(
    image_path, polygon_count, vertices_count,
    population_size=6,
    max_internal_size=(200, 200),
    print_cycle=50
)

# NOTE these paths consider that you're running on the same directory as this file
#      also, the min_fitness value to save the DNA should be changed depending on the fitness function

save_path = "generated" # os.path.join("generated", image_name)

(runner
    # .save_dna_to(os.path.join(save_path, "dna"), min_fitness=100_000_000)
    .save_best_to(save_path, save_cycle=4_000)
    .save_all_to(save_path, save_cycle=10_000)
    .show_at(show_cycle=10, show_all=True)
    .plot_at(plot_cycle=10, plot_time_on_x=False, show_plot=True, save_plot=True, save_path=os.path.join(save_path, "plot"))
    .set_fitness_func(FitnessCalculator(runner.image).ssd)
    # .set_bg_color(WHITE)
    .set_mutation_rate(0.6)
    .set_crossover_rate(0.3)
    .set_selection_strategy('truncation') # 'first_packs', 'truncation', 'stochastic_acceptance', 'roulette_wheel'
    .set_crossover_strategy('uniform') # 'single_point', 'single_point_stochastic', 'uniform'
    .set_substitution_method('comma_selection') # 'plus_selection', 'comma_selection', 'tournament'
    .set_mutation_params(hard_mutation_fitness_limit=150_000_000, random_hard_mutation_prob=0.005)
    # .halt_on(max_unimproved_cycles=None, fitness_limit=None, duration_limit=None)

).run(use_image_colors=True)