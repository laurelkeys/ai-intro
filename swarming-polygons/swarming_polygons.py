import numpy as np
from sys import argv
from time import time
from PIL import Image, ImageDraw

# ______________________________________________________________________________
class Colony:
    def __init__(self, image, polygon_count, vertex_count):
        self.original_image_array = np.array(image.copy())
        self.width = image.size[0]
        self.height = image.size[1]

        self.polygon_count = polygon_count
        self.vertex_count = vertex_count

        self.colors = np.random.randint(0, 256, size=(polygon_count, 4), dtype=np.dtype('uint8')) # RGBA

        self.polygons = np.empty((polygon_count, 2 * vertex_count), dtype=np.dtype('int'))
        self.polygons[:, 0::2] = np.random.randint(0, self.width, size=(polygon_count, vertex_count)) # x values on even positions
        self.polygons[:, 1::2] = np.random.randint(0, self.height, size=(polygon_count, vertex_count)) # y values on odd positions
        
        self.edges = np.tile([self.width, self.height], vertex_count) # FIXME

        self.best = np.array(self.draw(self.colors, self.polygons)) # image_array
        self.best_fitness = self.calculate_fitness(self.best)
    
    def draw(self, colors, polygons):
        canvas = Image.new('RGB', (self.width, self.height), (255, 255, 255, 0))
        drawer = ImageDraw.Draw(canvas, 'RGBA')
        for color, polygon in zip(colors, polygons):
            drawer.polygon(polygon[:].tolist(), tuple(color)) # FIXME check if copying is needed
        del(drawer) # TODO verify if del is necessary (and if not recreating it each time improves performance)
        return canvas
    
    def calculate_fitness(self, image_array):
        return np.abs(np.subtract(self.original_image_array, image_array, dtype=np.dtype('i4'))).sum()
        # return np.square(np.subtract(self.original_image_array, image_array, dtype=np.dtype('i4'))).sum()
    
    def mutant(self):

        def mutate_vertex(self, polygon_index):
            # FIXME
            # colors = self.colors.copy()
            polygons = self.polygons.copy()
            max_dim = max(self.width, self.height)
            vertex_perturbation = np.random.randint(- max_dim/2, (max_dim/2) + 1, size=2) # (dx, dy) perturbations for mutation
            vertex_index = 2 * np.random.choice(self.vertex_count) # chooses one of the polygon's vertices to mutate
            polygons[polygon_index, vertex_index:vertex_index+2] = np.clip(a=polygons[vertex_index, vertex_index:vertex_index+2] + vertex_perturbation, 
                                                                           a_min=0, 
                                                                           a_max=[self.width, self.height])
            # return colors, polygons
            return self.colors, polygons

        def mutate_polygon(self, polygon_index):
            # FIXME
            # colors = self.colors.copy()
            polygons = self.polygons.copy()
            max_dim = max(self.width, self.height)
            polygon_perturbation = np.tile(np.random.randint(- max_dim/2, (max_dim/2) + 1, size=2), self.vertex_count)
            polygons[polygon_index] = np.clip(a=polygons[polygon_index] + polygon_perturbation, 
                                              a_min=0, 
                                              a_max=self.edges)
            # return colors, polygons
            return self.colors, polygons

        def mutate_color(self, polygon_index):
            # FIXME
            colors = self.colors.copy()
            # polygons = self.polygons.copy()
            color_perturbation = np.random.randint(-255, 256, size=3) # RGB
            colors[polygon_index][:3] = np.clip(colors[polygon_index][:3] + color_perturbation, 0, 255)
            # return colors, polygons
            return colors, self.polygons

        def mutate_alpha(self, polygon_index):
            # FIXME
            colors = self.colors.copy()
            # polygons = self.polygons.copy()
            alpha_perturbation = np.random.randint(-255, 256)
            colors[polygon_index][3] = np.clip(colors[polygon_index][3] + alpha_perturbation, 0, 255)
            # return colors, polygons
            return colors, self.polygons

        mutation = np.random.choice([mutate_vertex, mutate_polygon, mutate_color, mutate_alpha])
        polygon_index = np.random.randint(self.polygon_count)
        return mutation(self, polygon_index)

    def search(self):
        new_colors, new_polygons = self.mutant()
        new_image_array = np.array(self.draw(new_colors, new_polygons))
        new_fitness = self.calculate_fitness(new_image_array)
        if new_fitness < self.best_fitness: # NOTE the lower the fitness (= objective function) the better
            self.colors = new_colors
            self.polygons = new_polygons
            self.best = new_image_array
            self.best_fitness = new_fitness
        return self.colors, self.polygons, self.best, self.best_fitness

    def save_best(self, save_path, save_format):
        image = self.draw(self.colors, self.polygons)
        image.save(save_path, save_format)

# ______________________________________________________________________________
try:
    image_path = argv[1]
    polygon_count = int(argv[2])
    vertex_count = 3 if len(argv) <= 3 else int(argv[3])
    max_cycles = -1 if len(argv) <= 4 else int(argv[4])
    assert(polygon_count > 0), "polygon_count must be positive"
    assert(vertex_count >= 3), "vertex_count must be at least 3"
except:
    print("usage: python swarming_polygons.py image_path polygon_count [vertex_count] [max_cycles]")
    exit()

image = Image.open(image_path).convert('RGB') # (3x8-bit pixels, true color)
image_size = image.size[0] * image.size[1] * 255 * 3
error = lambda fitness: fitness / image_size * 100

colony = Colony(image=image,
                polygon_count=polygon_count,
                vertex_count=vertex_count)

cycle = 0
start_time = time()
try:
    while cycle < max_cycles or max_cycles < 0:
        if cycle % 5000 == 0:
            print(f"Cycle {cycle:>8}: error = {error(colony.best_fitness):>7.4f}% (Δt = {(time() - start_time):>7.2f}s)")
            if cycle % 10000 == 0:
                colony.save_best(f"nectar{cycle}.png", 'PNG')
        colony.search() # iterates a cycle, returns (colors, polygons, image_array, fitness)
        cycle += 1
except:
    end_time = time()
    save_image_path = "nectar.png"
    print(f"Cycle {cycle:>8}: error = {error(colony.best_fitness):>7.4f}% (Δt = {(end_time - start_time):>7.2f}s)")
    print(f"\nSaved solution at {save_image_path}")
    print(f"[cycle|time|fitness|polygons|vertices]=[{cycle}|{(end_time - start_time):.2f}|{colony.best_fitness}|{polygon_count}|{vertex_count}]")
    colony.save_best(save_image_path, 'PNG')
else:
    end_time = time()
    save_image_path = "nectar.png"
    print(f"Cycle {cycle:>8}: error = {error(colony.best_fitness):>7.4f}% (Δt = {(end_time - start_time):>7.2f}s)")
    print(f"Saved the best found solution at {save_image_path}")
    print(f"[polygons|vertices|cycle|time|fitness]=[{polygon_count}|{vertex_count}|{cycle}|{end_time - start_time}|{colony.best_fitness}]")
    colony.save_best(save_image_path, 'PNG')

# TODO:
#  - make a Polygon class
#  - allow "starting points" other than a random canvas
#  - save the best solution's 'colors' and 'polygons' to use as a starting point
#  - test different fitness functions
#  - improve performance:
#      - of used functions
#      - using new methods
#  - enable image rendering in higher resolutions based on 'polygons'