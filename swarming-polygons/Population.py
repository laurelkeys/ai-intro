import copy

from Pack import WHITE, Pack

class Population:
    def __init__(self, width, height, polygon_count, vertices_count, fitness_func, dna_path=None, bg_color=WHITE, population_size=1):
        self.population_size = population_size # equal to the number of packs (one pack <=> one image)
        if dna_path == None:
            self.packs = [Pack(width, height, polygon_count, vertices_count, fitness_func, bg_color=bg_color) for _ in range(population_size)]
        else:
            # puts the given Pack (through it's DNA) on self.packs
            self.packs = [Pack(width, height, polygon_count, vertices_count, fitness_func, dna_path=dna_path, bg_color=bg_color)]
            for _ in range(population_size - 1):
                self.packs.append(Pack(width, height, polygon_count, vertices_count, fitness_func, bg_color=bg_color))
        
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