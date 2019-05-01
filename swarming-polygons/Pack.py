import copy
import pickle

import numpy as np
from PIL import Image, ImageDraw

WHITE = (255, 255, 255) # (red, green, blue[, alpha])

class Pack:
    def __init__(self, width, height, polygon_count, vertices_count, fitness_func, dna_path=None, bg_color=WHITE, fix_alpha=False, fix_alpha_value=128):
        self.width = width
        self.height = height
        self.vertices_count = vertices_count
     
        if dna_path == None:
            if fix_alpha:
                self.colors = np.empty((polygon_count, 4), dtype=np.uint8)
                self.colors[:, :3] = np.random.randint(low=0, high=256, size=(polygon_count, 3), dtype=np.uint8) # RGB
                self.colors[:, 3] = np.full(shape=polygon_count, fill_value=fix_alpha_value) # Alpha
            else:
                self.colors = np.random.randint(low=0, high=256, size=(polygon_count, 4), dtype=np.uint8) # RGBA
            self.fix_alpha = fix_alpha

            self.polygons = np.empty((polygon_count, 2 * vertices_count), dtype=np.int16)
            self.polygons[:, 0::2] = np.random.randint(low=0, high=self.width, size=(polygon_count, vertices_count), dtype=np.int16) # x values on even positions
            self.polygons[:, 1::2] = np.random.randint(low=0, high=self.height, size=(polygon_count, vertices_count), dtype=np.int16) # y values on odd positions
            self.bg_color = bg_color
        else:
            self.__from_dna(dna_path) # inits self.colors, self.polygons, and self.bg_color        

        self.image = np.array(self.draw(self.colors, self.polygons), dtype=np.uint8)
        self.fitness = fitness_func(self.image)
    
    def draw(self, colors, polygons, scale=1):
        canvas = Image.new('RGB', (self.width * scale, self.height * scale), self.bg_color)
        drawer = ImageDraw.Draw(canvas, 'RGBA')
        for color, polygon in zip(colors, polygons):
            drawer.polygon((scale * polygon).tolist(), tuple(color))
        del drawer
        return canvas
    
    def mutant(self):

        mutate_alpha_range = (32, 196)

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
            colors[polygon_index, :3] = np.random.randint(0, 256, size=3, dtype=np.uint8) # RGB
            return colors, self.polygons

        def __mutate_alpha(self, polygon_index):
            colors = self.colors.copy()
            colors[polygon_index, 3] = np.random.randint(mutate_alpha_range[0], mutate_alpha_range[1], dtype=np.uint8) # Alpha
            return colors, self.polygons

        if self.fix_alpha:
            mutation = np.random.choice([__mutate_vertex, __mutate_polygon, __mutate_color])
        else:
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
        # NOTE a string representation can be seen with the following (use only for debugging):
        # return str(pickle.loads(pickle.dumps(dna_obj))) # == str(dna)
        dna_obj = {
            'width' : self.width,
            'height' : self.height,
            'vertices_count' : self.vertices_count,
            'colors' : self.colors,
            'polygons' : self.polygons,
            'bg_color' : self.bg_color
        }
        return pickle.dumps(dna_obj) # binary representation
    
    def __from_dna(self, dna_path):
        with open(dna_path, 'rb') as f:
            dna_obj = pickle.load(f)
        assert(dna_obj['width'] == self.width and dna_obj['height'] == self.height and dna_obj['vertices_count'] == self.vertices_count)
        self.colors = dna_obj['colors']
        self.polygons = dna_obj['polygons']
        self.bg_color = dna_obj['bg_color']
