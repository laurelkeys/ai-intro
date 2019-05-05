import os
from sys import argv
from time import time

import numpy as np
from PIL import Image

from utils import FitnessCalculator, avg_color
from Population import Population

# ______________________________________________________________________________
PRINT_CYCLE = 5000
SAVE_CYCLE = 10000

SAVE_ALL_PATH = os.path.join("images", "temp", "all.png")
SAVE_IMAGE_PATH = os.path.join("generated", "pack.png")
SAVE_DNA_PATH = os.path.join("generated", "dna.pkl")
INIT_DNA_PATH = os.path.join("generated", "init_dna.pkl") # DNA of a Pack to be added to the initial Population

POPULATION_SIZE = 1

# MAX_IMAGE_SIZE = (256, 256) # (width, height)
MAX_IMAGE_SIZE = (512, 512)

# ______________________________________________________________________________
try:
    image_path = argv[1]
    polygon_count = int(argv[2])
    vertices_count = 3 if len(argv) <= 3 else int(argv[3])
    max_cycles = -1 if len(argv) <= 4 else int(argv[4])
    assert(polygon_count >= 0 and polygon_count <= 255)
    assert(vertices_count >= 3 and vertices_count <= 255)
except:
    print("usage: python swarming_polygons.py image_path polygon_count [vertices_count] [max_cycles]")
    exit()

original_image = Image.open(image_path).convert('RGB')
scale = 1
if max(original_image.size) > max(MAX_IMAGE_SIZE):
    print(f"(height, width) = ({original_image.size[1]}, {original_image.size[0]}) resized to:")
    scale = int(max(original_image.size) / max(MAX_IMAGE_SIZE))
    original_image.thumbnail(MAX_IMAGE_SIZE) # keeps the image proportion

original_image = np.array(original_image, dtype=np.uint8)
height, width, *_ = original_image.shape
print(f"(height, width, depth) = {original_image.shape}")

fitness_func = FitnessCalculator(original_image).ssd
partial_fitness_func = FitnessCalculator(original_image).partial_ssd

population = Population(width, height, polygon_count, vertices_count, 
                        fitness_func=fitness_func,
                        dna_path=INIT_DNA_PATH if os.path.isfile(INIT_DNA_PATH) else None, # verifies if the file exists
                        bg_color=avg_color(original_image),
                        population_size=POPULATION_SIZE,
                        original_image=original_image) # uses original_image's colors on starting polygons

cycle = 0
start_time = time()
try:
    while max_cycles < 0 or cycle < max_cycles:
        if cycle % PRINT_CYCLE == 0:
            if cycle % SAVE_CYCLE == 0 and cycle != 0: 
                population.save_best_image(os.path.join("generated", f"{cycle}.png"))
                # population.save_all(os.path.join("generated", f"{cycle}-all.png"))
            print(f"[{cycle}:{population.best_pack_index}] fitness={population.best_fitness:_d}, Δt={(time() - start_time):.2f}s")
        population.cycle(fitness_func, partial_fitness_func) # iterates through a cycle
        cycle += 1
except:
    pass
finally:
    duration = time() - start_time
    print(f"[{cycle}:{population.best_pack_index}] fitness={population.best_fitness:_d}, Δt={duration:.2f}s")
    
    population.save_best_image(SAVE_IMAGE_PATH, scale=scale)
    print(f"\nSolution saved at {SAVE_IMAGE_PATH}")
    print(f"[polygons|vertices|fitness|cycle|time]=[{polygon_count}|{vertices_count}|{population.best_fitness:_d}|{cycle}|{duration:.2f}]")

    f = open(SAVE_DNA_PATH,"wb+") # binary file
    f.write(population.best_dna)
    f.close()
    print(f"\nSolution's DNA saved at {SAVE_DNA_PATH}")
    
    # population.save_all(SAVE_ALL_PATH)
