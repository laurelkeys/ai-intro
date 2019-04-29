import numpy as np
from sys import argv
from time import time
from PIL import Image, ImageDraw

WHITE = (255, 255, 255, 0)
PRINT_CYCLE = 5000
SAVE_CYCLE = 10000
SAVE_PATH = "pack.png"
DNA_PATH = "dna.txt"
POPULATION_SIZE = 1

# ______________________________________________________________________________
class Pack:
    def __init__(self, image, polygon_count, vertices_count, fitness_func):
        self.height, self.width, *_ = image.shape # image.shape == (height, width, depth)
        self.vertices_count = vertices_count

        self.colors = np.random.randint(low=0, high=256, size=(polygon_count, 4), dtype=np.dtype('uint8')) # RGBA

        self.polygons = np.empty((polygon_count, 2 * vertices_count), dtype=np.dtype('int16'))
        self.polygons[:, 0::2] = np.random.randint(low=0, high=self.width, size=(polygon_count, vertices_count)) # x values on even positions
        self.polygons[:, 1::2] = np.random.randint(low=0, high=self.height, size=(polygon_count, vertices_count)) # y values on odd positions

        self.image = np.array(self.draw(self.colors, self.polygons)) # image array
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
            polygons[polygon_index, vertex_index] = np.random.randint(low=0, high=self.width + 1, dtype=np.dtype('int16'))
            polygons[polygon_index, vertex_index + 1] = np.random.randint(low=0, high=self.height + 1, dtype=np.dtype('int16'))
            return self.colors, polygons

        def __mutate_polygon(self, polygon_index):
            polygons = self.polygons.copy()
            polygons[polygon_index, 0::2] = np.tile(np.random.randint(low=0, high=self.width + 1, dtype=np.dtype('int16')), self.vertices_count) # x's
            polygons[polygon_index, 1::2] = np.tile(np.random.randint(low=0, high=self.height + 1, dtype=np.dtype('int16')), self.vertices_count) # y's
            return self.colors, polygons

        def __mutate_color(self, polygon_index):
            colors = self.colors.copy()
            colors[polygon_index][:3] = np.random.randint(0, 256, size=3, dtype=np.dtype('uint8')) # RGB
            return colors, self.polygons

        def __mutate_alpha(self, polygon_index):
            colors = self.colors.copy()
            colors[polygon_index][3] = np.random.randint(26, 225, dtype=np.dtype('uint8')) # Alpha
            return colors, self.polygons

        mutation = np.random.choice([__mutate_vertex, __mutate_polygon, __mutate_color, __mutate_alpha])
        polygon_index = np.random.randint(self.polygons.shape[0]) # [0, polygons_count)
        return mutation(self, polygon_index)

    def cycle(self, fitness_func):
        child_colors, child_polygons = self.mutant()
        child_image = np.array(self.draw(child_colors, child_polygons))
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
# class Population:
#     def __init__(self, image, polygon_count, vertices_count, fitness_func, population_size=1):
#         self.packs = [Pack(image, polygon_count, vertices_count, fitness_func) for _ in range(population_size)]
#         self.best_pack = self.packs[0] # <=> best_image
#         self.best_fitness = self.best_pack.fitness
#



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

image = np.array(Image.open(image_path).convert('RGB')) # (3x8-bit pixels, true color)
assert(image.shape[0] <= 4096 and image.shape[1] <= 4096)

def fitness_ssd(pack_image):
    return np.square(np.subtract(image, pack_image, dtype=np.dtype('int16')).astype('int32')).sum() # sum square difference

pack = Pack(image, polygon_count, vertices_count, fitness_ssd)

cycle = 0
start_time = time()
try:
    while cycle < max_cycles or max_cycles < 0:
        if cycle % PRINT_CYCLE == 0:
            if cycle % SAVE_CYCLE == 0 and cycle != 0: pack.save_image(f"{cycle}.png", 'PNG')
            print(f"[{cycle}] fitness={pack.fitness}, Δt={(time() - start_time):.2f}s")
        pack.cycle(fitness_ssd) # iterates through a cycle
        cycle += 1
except:
    pass
finally:
    end_time = time()
    pack.save_image(SAVE_PATH, 'PNG')
    print(f"[{cycle}] fitness={pack.fitness}, Δt={(time() - start_time):.2f}s")
    print(f"\nSolution saved at {SAVE_PATH}")
    print(f"[polygons|vertices|fitness|cycle|time]=[{polygon_count}|{vertices_count}|{pack.fitness}|{cycle}|{(end_time - start_time):.2f}]")
    f = open(DNA_PATH,"w+")
    f.write(pack.dna)
    f.close()
    print(f"\nSolution's DNA saved at {DNA_PATH}")
