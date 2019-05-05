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
    population_size=1,
    max_internal_size=(512, 512), 
    print_cycle=5000
)

# NOTE these paths consider that you're running on the same directory as this file

runner.save_dna_to(save_path=os.path.join("generated", "dna")) \
    .save_best_to(save_path="generated", save_cycle=10000) \
    .save_all_to(save_path="generated") \
    .set_bg_color(WHITE) \
    .run(use_image_colors=False)

