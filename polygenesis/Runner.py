import os
from time import time

import numpy as np
from PIL import Image

from utils import FitnessCalculator, avg_color
from Population import Population
from Plotter import Plotter

class Runner:
    def __init__(self, image_path, polygon_count, vertices_count, population_size=1,
                 max_cycles=None, max_internal_size=(512, 512), print_cycle=5000):

        pil_image = Image.open(image_path).convert('RGB')
        self.original_size = pil_image.size
        if max(pil_image.size) > max(max_internal_size):
            pil_image.thumbnail(max_internal_size) # keeps proportions
        self.image = np.array(pil_image, dtype=np.uint8)
        # NOTE self.original_size == (width, height), while self.image.shape == (height, width, depth)

        self.polygon_count = polygon_count
        self.vertices_count = vertices_count
        self.population_size = population_size
        self.max_cycles = max_cycles
        self.print_cycle = print_cycle

        # default values (if not set)
        self.fitness_func = FitnessCalculator(self.image).sad
        self.random_hard_mutation_prob = 0.0
        self.mutation_rate = 1.0
        self.crossover_rate = 0.0
        self.selection_strategy = 'truncation'
        self.crossover_strategy = 'uniform'
        self.substitution_method = 'plus_selection'


    def __getattr__(self, name):
        return None # returns None when an attribute isn't found

    def save_dna_to(self, save_path, prefix='dna_', min_fitness=float('inf')):
        self.save_dna_path = save_path
        self.save_dna_prefix = prefix
        self.save_dna_min_fitness = min_fitness
        return self

    def save_best_to(self, save_path, save_cycle=None, prefix='', final_save_prefix='best_pack_'):
        self.save_best_path = save_path
        self.save_best_cycle = save_cycle
        self.save_best_prefix = prefix
        self.save_best_final_prefix = final_save_prefix
        return self

    def save_all_to(self, save_path, save_cycle=None, prefix='population_', final_save_prefix='final_population_'):
        self.save_all_path = save_path
        self.save_all_cycle = save_cycle
        self.save_all_prefix = prefix
        self.save_all_final_prefix = final_save_prefix
        return self

    def show_at(self, show_cycle=1, show_all=False):
        self.show_cycle = show_cycle
        self.show_all = show_all
        return self

    def plot_at(self, plot_cycle=1, plot_time_on_x=False, show_plot=False, save_plot=False, save_path=None, prefix='plot_'):
        self.plotter = Plotter(xlabel='Time' if plot_time_on_x else 'Cycle', show_plot=show_plot)
        self.plot_cycle = plot_cycle
        self.plot_time_on_x = plot_time_on_x
        self.show_plot = show_plot
        self.save_plot = save_plot
        self.save_plot_path = save_path
        self.save_plot_prefix = prefix
        return self

    def init_with(self, dna_path):
        self.initial_dna_path = dna_path # DNA of a Pack to be added to the initial Population
        return self

    def set_fitness_func(self, fitness_func):
        self.fitness_func = fitness_func
        return self

    def set_bg_color(self, bg_color):
        self.bg_color = bg_color
        return self
    
    def set_mutation_rate(self, rate):
        self.mutation_rate = rate
        return self
    
    def set_crossover_rate(self, rate):
        self.crossover_rate = rate
        return self
    
    def set_selection_strategy(self, selection_strategy):
        self.selection_strategy = selection_strategy
        return self
    
    def set_crossover_strategy(self, crossover_strategy):
        self.crossover_strategy = crossover_strategy
        return self
    
    def set_substitution_method(self, substitution_method):
        self.substitution_method = substitution_method
        return self

    def set_mutation_params(self, hard_mutation_fitness_limit=None, random_hard_mutation_prob=0.0):
        self.hard_mutation_fitness_limit = hard_mutation_fitness_limit # applies soft mutations once the best fitness is lower than this
        self.random_hard_mutation_prob = random_hard_mutation_prob # chance of a random hard mutation when applying soft mutations
        return self
    
    def set_max_unimproved_cycles(self, max_unimproved_cycles):
        self.max_unimproved_cycles = max_unimproved_cycles
        return self

    def halt_on(self, max_unimproved_cycles=None, fitness_limit=None, duration_limit=None):
        self.halt_on_max_unimproved_cycles = max_unimproved_cycles
        self.halt_on_fitness_limit = fitness_limit
        self.halt_on_duration_limit = duration_limit
        return self

    def run(self, use_image_colors=True):
        height, width, *_ = self.image.shape
        print(f"(height, width, depth) = {self.image.shape}", end='')
        print('' if sum(self.original_size) == sum(self.image.shape[0:2]) else f" [resized from {' by '.join(map(str, self.original_size))}]")

        population = Population(
            width, height,
            self.polygon_count, self.vertices_count,
            fitness_func=self.fitness_func,
            population_size=self.population_size,
            dna_path=self.initial_dna_path, # not used if None
            bg_color=self.bg_color if self.bg_color else avg_color(self.image), # not used if initial_colors_image is also passed
            initial_colors_image=self.image if use_image_colors else None # uses image's colors on starting polygons
        )

        self.cycle = 0
        start_time = time()

        should_cycle = lambda cycle: True if not self.max_cycles else cycle < self.max_cycles
        should_print = lambda cycle: cycle % self.print_cycle == 0
        should_save_best = lambda cycle: False if not self.save_best_cycle else cycle % self.save_best_cycle == 0
        should_save_all = lambda cycle: False if (not self.save_all_cycle) or (self.population_size <= 1) else cycle % self.save_all_cycle == 0
        should_show = lambda cycle: False if not self.show_cycle else cycle % self.show_cycle == 0
        should_plot = lambda cycle: False if not self.plot_cycle else cycle % self.plot_cycle == 0 or self.plot_cycle == 1
        should_hard_mutate = lambda fitness: (np.random.random() < self.random_hard_mutation_prob or 
                                             (False if not self.hard_mutation_fitness_limit else fitness >= self.hard_mutation_fitness_limit))
        
        unimproved_cycles = 0
        prev_best_fitness = None

        try:
            while should_cycle(self.cycle):
                population.iterate(self.fitness_func, 
                                   hard_mutation=should_hard_mutate(population.best_fitness),
                                   mutation_rate=self.mutation_rate, crossover_rate=self.crossover_rate,
                                   selection_strategy=self.selection_strategy, crossover_strategy=self.crossover_strategy,
                                   substitution_method=self.substitution_method)

                self.cycle += 1
                unimproved_cycles = 0 if population.best_fitness != prev_best_fitness else unimproved_cycles + 1
                prev_best_fitness = population.best_fitness
                curr_duration = time() - start_time
                if self.__should_halt(unimproved_cycles, prev_best_fitness, curr_duration):
                    break

                if should_print(self.cycle):
                    try: print(f"[{self.cycle}] fitness={population.best_fitness:_d}, Δt={(curr_duration):.2f}s")
                    except ValueError: print(f"[{self.cycle}] fitness={population.best_fitness:.2f}, Δt={(curr_duration):.2f}s")
                if should_save_best(self.cycle):
                    population.save_best(os.path.join(self.save_best_path, f"{self.save_best_prefix}{self.cycle}.png"))
                if should_save_all(self.cycle):
                    population.save_all(os.path.join(self.save_all_path, f"{self.save_all_prefix}{self.cycle}.png"))
                if should_show(self.cycle):
                    if self.show_all:
                        population.show_all()
                    else:
                        population.show_best() 
                if should_plot(self.cycle):
                    self.plotter.update(xdata=curr_duration if self.plot_time_on_x else self.cycle, 
                                        fitnesses=list(map(lambda pack: pack.fitness, population.packs)), 
                                        all_time_best=population.best_fitness)

        except(KeyboardInterrupt, SystemExit):
            pass

        finally:
            duration = time() - start_time
            try: print(f"[{self.cycle}] fitness={population.best_fitness:_d}, Δt={duration:.2f}s")
            except ValueError: print(f"[{self.cycle}] fitness={population.best_fitness:.2f}, Δt={duration:.2f}s")

            if self.save_best_path:
                save_path = os.path.join(self.save_best_path, f"{self.save_best_final_prefix}{self.cycle}.png")
                population.save_best(save_path)
                print(f"\nBest solution saved at {save_path}")
            
            if self.save_plot:
                self.plotter.save(save_path=self.save_plot_path, file_name=f"{self.save_plot_prefix}{'time_' if self.plot_time_on_x else 'cycle_'}{self.cycle}")

            if self.population_size > 1 and self.save_all_path:
                save_path = os.path.join(self.save_all_path, f"{self.save_all_final_prefix}{self.cycle}.png")
                population.save_all(save_path)
                print(f"\nFinal population saved at {save_path}")

            if self.save_dna_path and population.best_fitness < self.save_dna_min_fitness:
                save_path = os.path.join(self.save_dna_path, f"{self.save_dna_prefix}{self.cycle}.pkl")
                with open(save_path, "wb+") as f: # binary file
                    f.write(population.best_dna)
                print(f"\nBest solution's DNA saved at {save_path}")
    
    def __should_halt(self, unimproved_cycles, prev_best_fitness, curr_duration):
        if self.halt_on_max_unimproved_cycles != None and unimproved_cycles > self.halt_on_max_unimproved_cycles:
            print(f"\nHalting, {unimproved_cycles} consecutive unimproved cycles")
            return True        
        if self.halt_on_fitness_limit != None and prev_best_fitness <= self.halt_on_fitness_limit:
            print(f"\nHalting, {prev_best_fitness} fitness reached")
            return True
        if self.halt_on_duration_limit != None and curr_duration >= self.halt_on_duration_limit:
            print(f"\nHalting, {curr_duration:.2f} seconds passed")
            return True        
        return False
