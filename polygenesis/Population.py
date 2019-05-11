import cv2
import copy
import numpy as np
from math import ceil
from PIL import Image

from Pack import Pack
from utils import WHITE

class Population:
    def __init__(self, width, height, polygon_count, vertices_count, fitness_func, population_size=1, dna_path=None, bg_color=WHITE, initial_colors_image=None):
        self.population_size = population_size # equal to the number of packs (one pack <=> one image)
        self.polygon_count = polygon_count

        self.packs = [Pack(width, height, polygon_count, vertices_count, fitness_func, bg_color=bg_color, initial_colors_image=initial_colors_image) for _ in range(population_size - 1)]
        if dna_path is None:
            self.packs.append(Pack(width, height, polygon_count, vertices_count, fitness_func, bg_color=bg_color, initial_colors_image=initial_colors_image))
        else:
            self.packs.append(Pack(width, height, polygon_count, vertices_count, fitness_func, dna_path=dna_path)) # generates a Pack from it's DNA and adds it to self.packs

        index = 0
        best_fitness = self.packs[index].fitness
        worst_fitness = self.packs[index].fitness
        for i in range(1, population_size):
            curr_fitness = self.packs[i].fitness
            if curr_fitness < best_fitness:
                index = i
                best_fitness = curr_fitness
            if curr_fitness > worst_fitness:
                worst_fitness = curr_fitness
        self.best_pack = copy.deepcopy(self.packs[index]) # <=> best_image
        self.best_fitness = best_fitness # == self.best_pack.fitness
        self.worst_fitness = worst_fitness

        self.curr_cycle = 0

    def __crossover(self, fitness_func):
        mother_index = np.random.randint(0, self.population_size)
        potential_partners = [*range(0, self.population_size)]
        potential_partners.remove(mother_index)
        father_index = np.random.choice(potential_partners)

        child_pack = copy.deepcopy(self.packs[mother_index])
        chiasma_start = np.random.randint(self.polygon_count // 4, self.polygon_count // 2)
        chiasma_end = np.random.randint(chiasma_start, 3 * self.polygon_count // 4)

        worst_index = 0
        worst_fitness = self.packs[0].fitness
        for i in range(self.population_size):
            curr_fitness = self.packs[i].fitness
            if curr_fitness > worst_fitness:
                worst_fitness = curr_fitness
                worst_index = i

        for chiasma_locus in range(chiasma_start, chiasma_end + 1):
            child_pack.polygons[chiasma_locus] = self.packs[father_index].polygons[chiasma_locus]
            child_pack.colors[chiasma_locus] = self.packs[father_index].colors[chiasma_locus]

        child_pack.image = np.array(child_pack.draw(child_pack.colors, child_pack.polygons))
        child_pack.fitness = fitness_func(child_pack.image)

        if child_pack.fitness < worst_fitness:
            self.packs[worst_index] = child_pack


    def cycle(self, fitness_func, partial_fitness_func=None, prophase=True):
        index = 0
        best_fitness = self.best_fitness
        worst_fitness = self.packs[0].fitness
        for i in range(self.population_size):
            self.packs[i].cycle(fitness_func, partial_fitness_func)
            curr_fitness = self.packs[i].fitness
            if curr_fitness < best_fitness:
                index = i
                best_fitness = curr_fitness
            if curr_fitness > worst_fitness:
                worst_fitness = curr_fitness

        if prophase and self.population_size > 1:
            self.__crossover(fitness_func)

        if best_fitness < self.best_fitness:
            self.best_pack = copy.deepcopy(self.packs[index])
            self.best_fitness = best_fitness # == self.best_pack.fitness
        self.worst_fitness = worst_fitness
        self.curr_cycle += 1

    def save_best(self, save_path, save_format='PNG'):
        self.best_pack.save_image(save_path, save_format)

    def show_best(self):
        self.best_pack.show_image()

    def __draw_all(self):
        # draws every Pack in the population in a single image, ordered in two rows
        width = min(self.packs[0].width, 200)
        height = min(self.packs[0].height, 200)
        canvas = Image.new("RGB", (width * ceil(self.population_size / 2), 2 * height if self.population_size > 1 else height))
        for i in range(self.population_size):
            image = self.packs[i].draw(self.packs[i].colors, self.packs[i].polygons)
            image.thumbnail((width, height))
            x = i // 2 * width
            y = i % 2 * height # evens on the first row and odds on the second
            canvas.paste(image, (x, y, x + width, y + height))
        return canvas

    def save_all(self, save_path, save_format='PNG'):
        self.__draw_all().save(save_path, save_format)

    def show_all(self):
        cv2.imshow('image', cv2.cvtColor(np.array(self.__draw_all()), cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)

    def show_all_windows(self):
        for i in range(self.population_size):
            image = cv2.cvtColor(self.packs[i].image,cv2.COLOR_RGB2BGR)
            cv2.imshow(f"image {i}", image)
        cv2.waitKey(1)

    @property
    def best_dna(self):
        return self.best_pack.dna
