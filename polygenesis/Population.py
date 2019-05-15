import cv2
import copy
import numpy as np
from math import ceil
from PIL import Image
import pathlib
import os

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
        for i in range(1, population_size):
            curr_fitness = self.packs[i].fitness
            if curr_fitness < best_fitness:
                index = i
                best_fitness = curr_fitness
        self.best_pack = copy.deepcopy(self.packs[index]) # <=> best_image
        self.best_fitness = best_fitness # == self.best_pack.fitness

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
        for i in range(self.population_size):
            self.packs[i].cycle(fitness_func, partial_fitness_func)
            curr_fitness = self.packs[i].fitness
            if curr_fitness < best_fitness:
                index = i
                best_fitness = curr_fitness

        if prophase and self.population_size > 1:
            self.__crossover(fitness_func)

        if best_fitness < self.best_fitness:
            self.best_pack = copy.deepcopy(self.packs[index])
            self.best_fitness = best_fitness # == self.best_pack.fitness
        self.curr_cycle += 1

    def save_best(self, save_path, save_format='PNG'):
        directory = os.path.join(*((save_path.split("/"))[:-1]))
        pathlib.Path(f'{directory}').mkdir(parents=True, exist_ok=True) 

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
        directory = os.path.join(*((save_path.split("/"))[:-1]))
        pathlib.Path(f'{directory}').mkdir(parents=True, exist_ok=True) 

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
    
    def __reproduce(self, partner1, partner2, fitness_func, crossover_strategy='single_point'):
        child1 = copy.deepcopy(partner1)
        child2 = copy.deepcopy(partner2)
       
        if crossover_strategy == 'single_point':
            for locus in range(0, self.polygon_count // 2):
                child1.polygons[locus] = partner2.polygons[locus]
                child1.colors[locus] = partner2.colors[locus]
                child2.polygons[locus] = partner1.polygons[locus]
                child2.colors[locus] = partner1.colors[locus]
        elif crossover_strategy == 'single_point_stochastic':
            for locus in range(0, np.random.randint(0, self.polygon_count)):
                child1.polygons[locus] = partner2.polygons[locus]
                child1.colors[locus] = partner2.colors[locus]
                child2.polygons[locus] = partner1.polygons[locus]
                child2.colors[locus] = partner1.colors[locus]
        elif crossover_strategy == 'uniform':
            for locus in range(0, self.polygon_count):
                if np.random.random() < 0.5:
                    child1.polygons[locus] = partner2.polygons[locus]
                    child1.colors[locus] = partner2.colors[locus]
                    child2.polygons[locus] = partner1.polygons[locus]
                    child2.colors[locus] = partner1.colors[locus]
        else:
            raise ValueError(f"Unexpected crossover_strategy ('{crossover_strategy}')")
        
        child1.image = child1.draw(child1.colors, child1.polygons)
        child1.fitness = fitness_func(child1.image)
        child2.image = child2.draw(child2.colors, child2.polygons)
        child2.fitness = fitness_func(child2.image)
        return child1, child2

    def iterate(self, fitness_func, mutation_rate, crossover_rate, selection_strategy, crossover_strategy, substitution_method, hard_mutation=True):
        # both parents and children compete to stay alive (ES plus-selection)
        selection_pool = list()

        # selection and crossover
        if selection_strategy == 'first_packs':
            for i in range(0, int(crossover_rate * self.population_size)):
                child1, child2 = self.__reproduce(self.packs[i], self.packs[(i+1) % self.population_size], fitness_func, crossover_strategy)
                selection_pool.append(child1)
                selection_pool.append(child2)
        elif selection_strategy == 'truncation':
            selection_pool.sort(key=lambda pack: pack.fitness) # elitism
            for i in range(0, int(crossover_rate * self.population_size)):
                child1, child2 = self.__reproduce(self.packs[i], self.packs[(i+1) % self.population_size], fitness_func, crossover_strategy)
                selection_pool.append(child1)
                selection_pool.append(child2)
        elif selection_strategy == 'stochastic_acceptance':
            i = 0
            crossover_amount = 0
            while crossover_amount < int(crossover_rate * self.population_size):
                if np.random.random() < self.packs[i].fitness / self.best_fitness:
                    selection_pool.append(copy.deepcopy(self.packs[i]))
                    crossover_amount += 1
                i = (i + 1) % self.population_size
        elif selection_strategy == 'roulette_wheel':
            i = 0
            crossover_amount = 0
            fitness_sum = sum(pack.fitness for pack in self.packs)
            while crossover_amount < int(crossover_rate * self.population_size):
                if np.random.random() < self.packs[i].fitness / fitness_sum:
                    selection_pool.append(copy.deepcopy(self.packs[i]))
                    crossover_amount += 1
                i = (i + 1) % self.population_size
        else:
            raise ValueError(f"Unexpected selection_strategy ('{selection_strategy}')")

        # mutation
        selection_pool.extend(copy.deepcopy(self.packs)) # FIXME
        for i in range(0, len(selection_pool)):
            if np.random.random() < mutation_rate:
                selection_pool[i].mutate(fitness_func, hard_mutation)

        # substitution
        if substitution_method == 'plus_selection':
            selection_pool.extend(copy.deepcopy(self.packs)) # puts the unmutated parents in the selection pool
            selection_pool.sort(key=lambda pack: pack.fitness) # NOTE the lower the fitness (= objective function) the better
            self.packs = selection_pool[0 : self.population_size]
            if self.packs[0].fitness < self.best_fitness:
                self.best_pack = copy.deepcopy(self.packs[0])
                self.best_fitness = self.packs[0].fitness
        elif substitution_method == 'comma_selection':
            selection_pool.sort(key=lambda pack: pack.fitness) # NOTE the lower the fitness (= objective function) the better
            self.packs = selection_pool[0 : self.population_size]
            if self.packs[0].fitness < self.best_fitness:
                self.best_pack = copy.deepcopy(self.packs[0])
                self.best_fitness = self.packs[0].fitness
        elif substitution_method == 'tournament':
            k = 3 # k-ary tournament # TODO make an option to change it
            matches = np.random.choice(selection_pool, size=k*self.population_size)
            best_index = 0
            best_fitness = float('inf')
            for i in range(0, self.population_size):
                match = matches[k*i : k*i + k]
                self.packs[i] = min(match, key=lambda pack: pack.fitness) # NOTE the lower the fitness (= objective function) the better
                if self.packs[i].fitness < best_fitness:
                    best_index = i
                    best_fitness = self.packs[i].fitness
            if best_fitness < self.best_fitness:
                self.best_pack = copy.deepcopy(self.packs[best_index])
                self.best_fitness = best_fitness

        else:
            raise ValueError(f"Unexpected substitution_method ('{substitution_method}')")
