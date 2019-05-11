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
    population_size=1,
    max_internal_size=(200, 200),
    print_cycle=1_000
)

# NOTE these paths consider that you're running on the same directory as this file
#      also, the min_fitness value to save the DNA should be changed depending on the fitness function

(runner
    .save_dna_to(save_path=os.path.join("generated", "dna"), min_fitness=100_000_000)
    .save_best_to(save_path="generated", save_cycle=5_000)
    # .save_all_to(save_path="generated", save_cycle=10_000)
    # .show_at(show_cycle=1, show_all=True)
    .set_fitness_func(FitnessCalculator(runner.image).ssd,
                      partial_fitness_func=FitnessCalculator(runner.image).partial_ssd)
    # .set_bg_color(WHITE)
    .set_mutation_rate(1.0)
    .set_crossover_rate(0.5)
    .set_mutation_params(hard_mutation_fitness_limit=150_000_000, random_hard_mutation_prob=0.001)
).run(use_partial_fitness=False,
      use_image_colors=True)

# Runner functions and params:
# - save_dna_to (save_path, prefix='dna_', min_fitness=float('inf'))
# - save_best_to (save_path, save_cycle=None, prefix='', final_save_prefix='best_pack_')
# - save_all_to (save_path, save_cycle=None, prefix='population_', final_save_prefix='final_population_')
# - show_at (show_cycle=1, show_all=False)
# - set_fitness_func (fitness_func, partial_fitness_func=None)
# - init_with (dna_path)
# - set_bg_color (bg_color)
# - set_mutation_rate (rate)
# - set_crossover_rate (rate)
# - set_selection_strategy (selection_strategy)
# - set_substitution_method (substitution_method)
# - set_mutation_params (hard_mutation_fitness_limit=None, random_hard_mutation_prob=0.0)
