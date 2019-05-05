import cv2
import copy
import numpy as np
from math import ceil
from PIL import Image

from Pack import Pack
from utils import WHITE

class Population:
    def __init__(self, width, height, polygon_count, vertices_count, fitness_func, dna_path=None, bg_color=WHITE, population_size=1, original_image=None):
        self.population_size = population_size # equal to the number of packs (one pack <=> one image)
        if dna_path is None:
            self.packs = [Pack(width, height, polygon_count, vertices_count, fitness_func, bg_color=bg_color, original_image=original_image) for _ in range(population_size)]
        else:
            # generates a Pack from it's DNA and adds it to self.packs
            self.packs = [Pack(width, height, polygon_count, vertices_count, fitness_func, dna_path=dna_path, bg_color=bg_color)]
            for _ in range(population_size - 1):
                self.packs.append(Pack(width, height, polygon_count, vertices_count, fitness_func, bg_color=bg_color, original_image=original_image))

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

    def cycle(self, fitness_func, partial_fitness_func=None):
        index = 0
        best_fitness = self.best_fitness
        for i in range(self.population_size):
            self.packs[i].cycle(fitness_func, partial_fitness_func)
            curr_fitness = self.packs[i].fitness
            if curr_fitness < best_fitness:
                index = i
                best_fitness = curr_fitness
        if best_fitness < self.best_fitness:
            self.best_pack = copy.deepcopy(self.packs[index])
            self.best_fitness = best_fitness # == self.best_pack.fitness
            self.best_pack_index = index

    def save_best_image(self, save_path, save_format='PNG', scale=1):
        self.best_pack.save_image(save_path, save_format, scale)

    def show_best_image(self, scale=1):
        self.best_pack.show_image(scale)

    def save_all(self, save_path, save_format='PNG'):
        # saves every Pack in the population in a single image, ordered in two rows
        width = min(self.packs[0].width, 200)
        height = min(self.packs[0].height, 200)
        canvas = Image.new("RGB", (width * ceil(self.population_size / 2), 2 * height if self.population_size > 1 else height))
        for i in range(self.population_size):
            image = self.packs[i].draw(self.packs[i].colors, self.packs[i].polygons)
            image.thumbnail((width, height))
            x = i // 2 * width
            y = i % 2 * height # evens on the first row and odds on the second
            canvas.paste(image, (x, y, x + width, y + height))
        canvas.save(save_path, save_format)

    def show_all(self):
        # show every Pack in the population in a single image, ordered in two rows
        width = min(self.packs[0].width, 200)
        height = min(self.packs[0].height, 200)
        canvas = Image.new("RGB", (width * ceil(self.population_size / 2), 2 * height if self.population_size > 1 else height))
        for i in range(self.population_size):
            image = self.packs[i].draw(self.packs[i].colors, self.packs[i].polygons)
            image.thumbnail((width, height))
            x = i // 2 * width
            y = i % 2 * height # evens on the first row and odds on the second
            canvas.paste(image, (x, y, x + width, y + height))
        cv2.imshow('image', cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)

    def show_all_windows(self):
        for i in range(self.population_size):
            image = cv2.cvtColor(self.packs[i].image,cv2.COLOR_RGB2BGR)
            cv2.imshow(f"image {i}", image)
        cv2.waitKey(1)

    @property
    def best_dna(self):
        return self.best_pack.dna
