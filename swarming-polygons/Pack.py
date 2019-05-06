import copy
import pickle

import cv2
import numpy as np
from PIL import Image, ImageDraw
from utils import vertices_color_avg, vertices_color_mid, WHITE

class Pack:
    def __init__(self, width, height, polygon_count, vertices_count, fitness_func, dna_path=None, bg_color=WHITE, initial_colors_image=None, initial_colors_func=vertices_color_mid):
        self.width = width
        self.height = height
        self.vertices_count = vertices_count

        if dna_path is not None:
            self.__from_dna(dna_path) # inits self.colors, self.polygons, and self.bg_color
        else:
            self.polygons = np.empty((polygon_count, 2 * vertices_count), dtype=np.int16)
            self.polygons[:, 0::2] = np.random.randint(low=0, high=self.width, size=(polygon_count, vertices_count), dtype=np.int16) # x values on even positions
            self.polygons[:, 1::2] = np.random.randint(low=0, high=self.height, size=(polygon_count, vertices_count), dtype=np.int16) # y values on odd positions
            self.bg_color = bg_color
            if initial_colors_image is None:
                self.colors = np.random.randint(low=0, high=256, size=(polygon_count, 4), dtype=np.uint8) # RGBA
            else:
                self.colors = np.empty((polygon_count, 4), dtype=np.uint8)
                for i in range(polygon_count):
                    self.colors[i, :] = initial_colors_func(self.polygons[i], self.vertices_count, initial_colors_image)

        self.image = np.array(self.draw(self.colors, self.polygons), dtype=np.uint8)
        self.fitness = fitness_func(self.image)

    def draw(self, colors, polygons, scale=1):
        canvas = Image.new('RGB', (self.width * scale, self.height * scale), self.bg_color)
        drawer = ImageDraw.Draw(canvas, 'RGBA')
        for color, polygon in zip(colors, polygons):
            drawer.polygon((scale * polygon).tolist(), tuple(color))
        del drawer
        return canvas

    def mutant(self, return_vertices=False):

        mutate_color_delta = 26
        mutate_alpha_range = (32, 196)

        def __mutate_vertex(self, polygon_index):
            polygons = self.polygons.copy()
            vertex_index = 2 * np.random.randint(low=0, high=self.vertices_count) # chooses one of the polygon's vertices to mutate
            polygons[polygon_index, vertex_index] = np.random.randint(low=0, high=self.width + 1, dtype=np.int16)
            polygons[polygon_index, vertex_index + 1] = np.random.randint(low=0, high=self.height + 1, dtype=np.int16)
            if return_vertices:
                return self.colors, polygons, self.polygons[polygon_index, :], polygons[polygon_index, :]
            else:
                return self.colors, polygons

        def __mutate_polygon(self, polygon_index):
            polygons = self.polygons.copy()
            polygons[polygon_index, 0::2] = np.tile(np.random.randint(low=0, high=self.width + 1, dtype=np.int16), self.vertices_count) # x's
            polygons[polygon_index, 1::2] = np.tile(np.random.randint(low=0, high=self.height + 1, dtype=np.int16), self.vertices_count) # y's
            if return_vertices:
                return self.colors, polygons, self.polygons[polygon_index, :], polygons[polygon_index, :]
            else:
                return self.colors, polygons

        def __mutate_color(self, polygon_index):
            colors = self.colors.copy()
            # colors[polygon_index, :3] = np.random.randint(0, 256, size=3, dtype=np.uint8) # RGB
            color_mutation = np.random.randint(low=-mutate_color_delta, high=mutate_color_delta + 1, size=3, dtype=np.int8)
            colors[polygon_index, :3] = np.clip(np.add(colors[polygon_index, :3], color_mutation, dtype=np.int16), 0, 255).astype(np.uint8)
            if return_vertices:
                return colors, self.polygons, self.polygons[polygon_index, :], self.polygons[polygon_index, :]
            else:
                return colors, self.polygons

        def __mutate_alpha(self, polygon_index):
            colors = self.colors.copy()
            colors[polygon_index, 3] = np.random.randint(mutate_alpha_range[0], mutate_alpha_range[1], dtype=np.uint8) # Alpha
            if return_vertices:
                return colors, self.polygons, self.polygons[polygon_index, :], self.polygons[polygon_index, :]
            else:
                return colors, self.polygons

        mutation = np.random.choice([__mutate_vertex, __mutate_polygon, __mutate_color, __mutate_alpha])
        polygon_index = np.random.randint(self.polygons.shape[0]) # [0, polygons_count)
        return mutation(self, polygon_index)

    def cycle(self, fitness_func, partial_fitness_func=None):
        if partial_fitness_func is not None:
            child_colors, child_polygons, parent_vertices, child_vertices = self.mutant(return_vertices=True)
            child_image = np.array(self.draw(child_colors, child_polygons), dtype=np.uint8)
            child_fitness = partial_fitness_func(child_image, parent_vertices, child_vertices)
            parent_fitness = partial_fitness_func(self.image, parent_vertices, child_vertices)
            if child_fitness < parent_fitness: # NOTE the lower the fitness (= objective function) the better
                self.colors = child_colors
                self.polygons = child_polygons
                self.image = child_image
                self.fitness = fitness_func(self.image)
        else:
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

    def show_image(self, scale=1):
        cv2.imshow('image', cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)

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
