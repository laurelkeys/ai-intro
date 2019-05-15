import copy
import pickle

import pathlib
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
from utils import vertices_color_avg, vertices_color_mid, WHITE

class Pack:
    def __init__(self, width, height, polygon_count, vertices_count, fitness_func, dna_path=None, bg_color=WHITE, initial_colors_image=None, initial_colors_func=vertices_color_mid):
        self.width = width
        self.height = height
        self.polygon_count = polygon_count
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
                    self.colors[i] = initial_colors_func(self.polygons[i], self.vertices_count, initial_colors_image, alpha=100)

        self.image = np.array(self.draw(self.colors, self.polygons), dtype=np.uint8)
        self.fitness = fitness_func(self.image)

    def draw(self, colors, polygons, scale=1):
        canvas = Image.new('RGB', (self.width * scale, self.height * scale), self.bg_color)
        drawer = ImageDraw.Draw(canvas, 'RGBA')
        for color, polygon in zip(colors, polygons):
            drawer.polygon((scale * polygon).tolist(), tuple(color))
        del drawer
        return canvas

    def save_image(self, save_path, save_format, scale=1):
        directory, *_ = os.path.split(save_path)
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

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
    
    def mutate(self, fitness_func, hard_mutation=True):

        mutate_vertex_delta_x = self.width if hard_mutation else self.width // 8 + 1
        mutate_vertex_delta_y = self.height if hard_mutation else self.height // 8 + 1
        mutate_color_delta = 255 if hard_mutation else 32
        mutate_alpha_range = (32, 196)
        mutate_order_delta = self.polygon_count if hard_mutation else self.polygon_count // 10  + 1

        def __mutate_vertex(polygon_index, vertex_index=None):
            if vertex_index == None:
                vertex_index = 2 * np.random.randint(low=0, high=self.vertices_count) # chooses one of the polygon's vertices to mutate

            perturbation_x = np.random.randint(low=-mutate_vertex_delta_x, high=mutate_vertex_delta_x + 1, dtype=np.int16)
            perturbation_x = np.add(self.polygons[polygon_index, vertex_index], perturbation_x, dtype=np.int16)
            self.polygons[polygon_index, vertex_index] = np.clip(perturbation_x, a_min=0, a_max=self.width - 1)

            perturbation_y = np.random.randint(low=-mutate_vertex_delta_y, high=mutate_vertex_delta_y + 1, dtype=np.int16)
            perturbation_y = np.add(self.polygons[polygon_index, vertex_index + 1], perturbation_y, dtype=np.int16)
            self.polygons[polygon_index, vertex_index + 1] = np.clip(perturbation_y, a_min=0, a_max=self.height - 1)

        def __mutate_polygon(polygon_index):
            for vertex_index in range(0, self.vertices_count):
                __mutate_vertex(polygon_index, 2 * vertex_index)

        def __mutate_color(polygon_index):
            perturbation = np.random.randint(low=-mutate_color_delta, high=mutate_color_delta + 1, size=3, dtype=np.int16)
            perturbation = np.add(self.colors[polygon_index, :3], perturbation, dtype=np.int16)
            self.colors[polygon_index, :3] = np.clip(perturbation, a_min=0, a_max=255).astype(np.uint8)

        def __mutate_alpha(polygon_index):
            self.colors[polygon_index, 3] = np.random.randint(mutate_alpha_range[0], mutate_alpha_range[1], dtype=np.uint8) # Alpha

        def __mutate_order(polygon_index):
            other_polygon_index = (polygon_index + np.random.randint(low=-mutate_order_delta, high=mutate_order_delta + 1)) % self.polygon_count
            if polygon_index == other_polygon_index:
                other_polygon_index = (other_polygon_index + 1) % self.polygon_count # chooses another polygon to swap drawing orders with

            self.polygons[polygon_index], self.polygons[other_polygon_index] = self.polygons[other_polygon_index], self.polygons[polygon_index]

        do_mutate = np.random.choice([__mutate_vertex, __mutate_polygon, __mutate_color, __mutate_alpha, __mutate_order])
        polygon_index = np.random.randint(self.polygon_count)
        # polygon_copy = copy.deepcopy(self.polygons[polygon_index, :])
        do_mutate(polygon_index)
        self.image = np.array(self.draw(self.colors, self.polygons))
        self.fitness = fitness_func(self.image)
        # return polygon_copy, self.polygons[polygon_index, :] # original vertices, mutated vertices
