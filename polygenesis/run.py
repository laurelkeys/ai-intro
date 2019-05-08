import os
from sys import argv
from Runner import Runner
from utils import WHITE, BLACK

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
    population_size=10,
    max_internal_size=(100, 100), 
    print_cycle=2_500,
    max_cycles=120_000
)

# NOTE these paths consider that you're running on the same directory as this file
runner \
    .save_dna_to(save_path=os.path.join("generated", "dna"), min_fitness=100_000_000) \
    .save_all_to(save_path="generated", save_cycle=5_000) \

runner.run(use_partial_fitness=False, use_image_colors=True)

# Runner functions and params:
# - save_dna_to (save_path, prefix='dna_', min_fitness=float('inf'))
# - save_best_to (save_path, save_cycle=None, prefix='', final_save_prefix='best_pack_')
# - save_all_to (save_path, save_cycle=None, prefix='population_', final_save_prefix='final_population_')
# - show_at (show_cycle=1, show_best_only=True)
# - set_fitness_func (fitness_func, partial_fitness_func=None)
# - init_with (dna_path)
# - set_bg_color (bg_color)
