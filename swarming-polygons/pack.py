import os
import copy
import numpy as np
from sys import argv
from time import time
from PIL import Image, ImageDraw

# ______________________________________________________________________________
POPULATION_SIZE = 1

PRINT_CYCLE = 5000
SAVE_CYCLE = 10000
SAVE_PATH = os.path.join("generated", "pack.png")
DNA_PATH = os.path.join("generated", "dna.txt")

WHITE = (255, 255, 255, 0)

# ______________________________________________________________________________
class Pack:
    def __init__(self, width, height, polygon_count, vertices_count, fitness_func):
        self.width = width
        self.height = height
        self.vertices_count = vertices_count

        self.colors = np.random.randint(low=0, high=256, size=(polygon_count, 4), dtype=np.uint8) # RGBA

        self.polygons = np.empty((polygon_count, 2 * vertices_count), dtype=np.int16)
        self.polygons[:, 0::2] = np.random.randint(low=0, high=self.width, size=(polygon_count, vertices_count), dtype=np.int16) # x values on even positions
        self.polygons[:, 1::2] = np.random.randint(low=0, high=self.height, size=(polygon_count, vertices_count), dtype=np.int16) # y values on odd positions

        self.image = np.array(self.draw(self.colors, self.polygons), dtype=np.uint8)
        self.fitness = fitness_func(self.image)
    
    def draw(self, colors, polygons, scale=1):
        canvas = Image.new('RGB', (self.width * scale, self.height * scale), color=WHITE)
        drawer = ImageDraw.Draw(canvas, 'RGBA')
        for color, polygon in zip(colors, polygons):
            drawer.polygon((scale * polygon).tolist(), tuple(color))
        del drawer
        return canvas
    
    def mutant(self):

        def __mutate_vertex(self, polygon_index):
            polygons = self.polygons.copy()
            vertex_index = 2 * np.random.randint(low=0, high=self.vertices_count) # chooses one of the polygon's vertices to mutate
            polygons[polygon_index, vertex_index] = np.random.randint(low=0, high=self.width + 1, dtype=np.int16)
            polygons[polygon_index, vertex_index + 1] = np.random.randint(low=0, high=self.height + 1, dtype=np.int16)
            return self.colors, polygons

        def __mutate_polygon(self, polygon_index):
            polygons = self.polygons.copy()
            polygons[polygon_index, 0::2] = np.tile(np.random.randint(low=0, high=self.width + 1, dtype=np.int16), self.vertices_count) # x's
            polygons[polygon_index, 1::2] = np.tile(np.random.randint(low=0, high=self.height + 1, dtype=np.int16), self.vertices_count) # y's
            return self.colors, polygons

        def __mutate_color(self, polygon_index):
            colors = self.colors.copy()
            colors[polygon_index][:3] = np.random.randint(0, 256, size=3, dtype=np.uint8) # RGB
            return colors, self.polygons

        def __mutate_alpha(self, polygon_index):
            colors = self.colors.copy()
            colors[polygon_index][3] = np.random.randint(26, 225, dtype=np.uint8) # Alpha
            return colors, self.polygons

        mutation = np.random.choice([__mutate_vertex, __mutate_polygon, __mutate_color, __mutate_alpha])
        polygon_index = np.random.randint(self.polygons.shape[0]) # [0, polygons_count)
        return mutation(self, polygon_index)

    def cycle(self, fitness_func):
        child_colors, child_polygons = self.mutant()
        child_image = np.array(self.draw(child_colors, child_polygons), dtype=np.uint8)
        child_fitness = fitness_func(child_image)
        if child_fitness < self.fitness: # NOTE the lower the fitness (= objective function) the better
            self.colors = child_colors
            self.polygons = child_polygons
            self.image = child_image
            self.fitness = child_fitness

    def save_image(self, save_path, save_format, scale=1):
        image = self.draw(self.colors, self.polygons, scale)
        image.save(save_path, save_format)

    @property
    def dna(self):
        # "(width,height,vertices_count)[(r,g,b,a)[x,y,...]...]", where (r,g,b,a)[x,y,...] is the polygon's DNA
        dna = f"({self.width},{self.height},{self.vertices_count})["
        for color, polygon in zip(self.colors, self.polygons):
            dna += f"({','.join(map(lambda i: hex(i)[2:], color))})"
            dna += f"[{','.join(map(str, polygon))}]"
        dna += "]"
        return dna

# ______________________________________________________________________________
class Population:
    def __init__(self, width, height, polygon_count, vertices_count, fitness_func, population_size=1):
        self.population_size = population_size # equal to the number of packs (one pack <=> one image)
        self.packs = [Pack(width, height, polygon_count, vertices_count, fitness_func) for _ in range(population_size)]
        
        index = 0
        best_fitness = self.packs[index].fitness
        for i in range(1, population_size):
            curr_fitness = self.packs[i].fitness
            if curr_fitness < best_fitness:
                index = i
                best_fitness = curr_fitness
        self.best_pack = copy.deepcopy(self.packs[index]) # <=> best_image
        self.best_fitness = best_fitness # == self.best_pack.fitness
        self.best_pack_index = index

    def cycle(self, fitness_func):
        index = 0
        best_fitness = self.best_fitness
        for i in range(self.population_size):
            self.packs[i].cycle(fitness_func)
            curr_fitness = self.packs[i].fitness
            if curr_fitness < best_fitness:
                index = i
                best_fitness = curr_fitness
        if best_fitness < self.best_fitness:
            self.best_pack = copy.deepcopy(self.packs[index])
            self.best_fitness = best_fitness # == self.best_pack.fitness
            self.best_pack_index = index

    def save_best_image(self, save_path, save_format, scale=1):
        self.best_pack.save_image(save_path, save_format, scale)

    @property
    def best_dna(self):
        return self.best_pack.dna

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

original_image = np.array(Image.open(image_path).convert('RGB'), dtype=np.uint8) # (3x8-bit pixels, true color)
height, width, *_ = original_image.shape # original_image.shape == (height, width, depth)
assert(height <= 4096 and width <= 4096)

def fitness_ssd(pack_image):
     # FIXME since the image's values are in [0, 255], the square might be doable with np.uint16
    return np.square(np.subtract(original_image, pack_image, dtype=np.int16), dtype=np.int32).sum() # sum square difference

population = Population(width, height, polygon_count, vertices_count, fitness_ssd, POPULATION_SIZE)

cycle = 0
start_time = time()
try:
    while cycle < max_cycles or max_cycles < 0:
        if cycle % PRINT_CYCLE == 0:
            if cycle % SAVE_CYCLE == 0 and cycle != 0: population.save_best_image(os.path.join("generated", f"{cycle}.png"), 'PNG')
            print(f"[{cycle}:{population.best_pack_index}] fitness={population.best_fitness}, Δt={(time() - start_time):.2f}s")
        population.cycle(fitness_ssd) # iterates through a cycle
        cycle += 1
except:
    pass
finally:
    end_time = time()
    population.save_best_image(SAVE_PATH, 'PNG')
    print(f"[{cycle}:{population.best_pack_index}] fitness={population.best_fitness}, Δt={(time() - start_time):.2f}s")
    print(f"\nSolution saved at {SAVE_PATH}")
    print(f"[polygons|vertices|fitness|cycle|time]=[{polygon_count}|{vertices_count}|{population.best_fitness}|{cycle}|{(end_time - start_time):.2f}]")
    f = open(DNA_PATH,"w+")
    f.write(population.best_dna)
    f.close()
    print(f"\nSolution's DNA saved at {DNA_PATH}")
