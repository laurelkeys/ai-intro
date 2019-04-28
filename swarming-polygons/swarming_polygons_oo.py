import numpy as np
from sys import argv
from time import time
from PIL import Image, ImageDraw

# ______________________________________________________________________________
class Polygon:
    def __init__(self, width, height, vertex_count, vertices=None, rgba_color=None):
        self.image_size = np.array([width, height], dtype=np.dtype('uint16'))
        self.vertex_count = vertex_count # equal to len(vertices)
        self.vertices = vertices
        self.color = rgba_color # 4-tuple (R, G, B, Alpha)

        if vertices == None:
            self.vertices = np.empty(shape=2*vertex_count, dtype=np.dtype('uint16')) # [x1, y1, x2, y2, .., xn, yn]
            self.vertices[0::2] = np.random.randint(low=0, high=width + 1, size=vertex_count, dtype=np.dtype('uint16')) # x values on even positions
            self.vertices[1::2] = np.random.randint(low=0, high=height + 1, size=vertex_count, dtype=np.dtype('uint16')) # y values on odd positions

        assert(self.vertices.size == 2*vertex_count)

        if rgba_color == None:
            self.color = np.random.randint(low=0, high=256, size=4, dtype=np.dtype('uint8')) # RGBA

    def mutate(self):

        def __mutate_vertex(self):
            vertex_index = 2 * np.random.choice(self.vertex_count) # chooses one of the polygon's vertices to mutate
            self.vertices[vertex_index] = np.random.randint(low=0, high=self.image_size[0] + 1, dtype=np.dtype('uint16'))
            self.vertices[vertex_index + 1] = np.random.randint(low=0, high=self.image_size[1] + 1, dtype=np.dtype('uint16'))

        def __mutate_polygon(self):
            self.vertices[0::2] = np.random.randint(low=0, high=self.image_size[0] + 1, size=self.vertex_count, dtype=np.dtype('uint16'))
            self.vertices[1::2] = np.random.randint(low=0, high=self.image_size[1] + 1, size=self.vertex_count, dtype=np.dtype('uint16'))

        def __mutate_color(self):
            self.color[:3] = np.random.randint(low=0, high=256, size=3, dtype=np.dtype('uint8')) # RGB

        def __mutate_alpha(self):
            self.color[3] = np.random.randint(low=0, high=256, dtype=np.dtype('uint8')) # Alpha

        func = np.random.choice([__mutate_vertex, __mutate_polygon, __mutate_color, __mutate_alpha]) # TODO change mutation types probabilities
        func(self)

# ______________________________________________________________________________
class Colony:
    def __init__(self, image, polygon_count, min_vertex_count, max_vertex_count=None):
        self.original_image_array = np.array(image)
        self.width = image.size[0]
        self.height = image.size[1]

        self.polygon_count = polygon_count
        self.min_vertex_count = min_vertex_count
        self.max_vertex_count = max_vertex_count if max_vertex_count != None else min_vertex_count

        self.polygons = [Polygon(image.size[0], image.size[1], vertex_count=np.random.randint(min_vertex_count, self.max_vertex_count + 1)) for _ in range(polygon_count)]

        self.best = np.array(self.draw(self.polygons)) # image array
        self.best_fitness = self.calculate_fitness(self.best)
    
    def draw(self, polygons, scale=1):
        canvas = Image.new('RGB', (self.width*scale, self.height*scale), (255, 255, 255, 0))
        drawer = ImageDraw.Draw(canvas, 'RGBA')
        for polygon in polygons:
            drawer.polygon(polygon.vertices.tolist(), tuple(polygon.color))
        del drawer
        return canvas

    def calculate_fitness(self, image_array):
        return np.square(np.subtract(self.original_image_array, image_array, dtype=np.dtype('uint16'))).sum()

    def search(self):
        child = self.polygons.copy()
        child[np.random.randint(self.polygon_count)].mutate()
        child_image_array = np.array(self.draw(child))
        child_fitness = self.calculate_fitness(child_image_array)
        if child_fitness < self.best_fitness: # NOTE the lower the fitness (= objective function) the better
            self.polygons = child
            self.best = child_image_array
            self.best_fitness = child_fitness

    def save_best(self, save_path, save_format, scale=1):
        image = self.draw(self.polygons, scale)
        image.save(save_path, save_format)

# ______________________________________________________________________________
try:
    image_path = argv[1]
    polygon_count = int(argv[2])
    min_vertex_count = 3 if len(argv) <= 3 else int(argv[3])
    if len(argv) == 5:
        max_vertex_count = int(argv[4])
        max_cycles = int(argv[5])
    else:
        max_vertex_count = min_vertex_count
        max_cycles = -1 if len(argv) <= 4 else int(argv[4])
except:
    print("usage: python swarming_polygons.py image_path polygon_count [min_vertex_count [max_vertex_count]] [max_cycles]")
    exit()

image = Image.open(image_path).convert('RGB') # (3x8-bit pixels, true color)
image_size = image.size[0] * image.size[1] * 255 * 3
error = lambda fitness: fitness / image_size * 100

colony = Colony(image=image,
                polygon_count=polygon_count,
                min_vertex_count=min_vertex_count,
                max_vertex_count=max_vertex_count)

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
    pass
finally:
    end_time = time()
    save_image_path = "nectar.png"
    print(f"Cycle {cycle:>8}: error = {error(colony.best_fitness):>7.4f}% (Δt = {(end_time - start_time):>7.2f}s)")
    print(f"\nSaved solution at {save_image_path}")
    print(f"[cycle|time|fitness|polygons|vertices]=[{cycle}|{(end_time - start_time):.2f}|{colony.best_fitness}|{polygon_count}|{vertex_count}]")
    colony.save_best(save_image_path, 'PNG')
