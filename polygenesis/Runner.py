import os
from time import time

import numpy as np
import statistics
import matplotlib.pyplot as plt
from PIL import Image

from utils import FitnessCalculator, avg_color
from Population import Population

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
    
    def save_plot_to(self, save_path, prefix='plot_'):
        self.save_plot_path = save_path
        self.save_plot_prefix = prefix
        return self

    def show_at(self, show_cycle=1, show_all=False):
        self.show_cycle = show_cycle
        self.show_all = show_all
        return self

    def plot_at(self, plot_cycle=1, plot_time_on_x=False):
        self.plot_cycle = plot_cycle
        self.plot_time_on_x = plot_time_on_x
        return self

    def init_with(self, dna_path):
        self.initial_dna_path = dna_path # DNA of a Pack to be added to the initial Population
        return self

    def set_fitness_func(self, fitness_func, partial_fitness_func=None):
        self.fitness_func = fitness_func
        self.partial_fitness_func = partial_fitness_func
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
        self.hard_mutation_fitness_limit = hard_mutation_fitness_limit
        self.random_hard_mutation_prob = random_hard_mutation_prob
        return self
    
    def set_max_unimproved_cycles(self, max_unimproved_cycles):
        self.max_unimproved_cycles = max_unimproved_cycles
        return self

    def run(self, use_partial_fitness=True, use_image_colors=True):
        height, width, *_ = self.image.shape

        if self.plot_cycle != None: 
            plot_avg, *_ = plt.plot([], [])
            plot_best, *_ = plt.plot([], [], linestyle=':')
            plot_worst, *_ = plt.plot([], [], linestyle=':')
            plot_avg.set_color("orange")
            plot_best.set_color("blue")
            plot_worst.set_color("red")
            fig = plt.gcf()
            fig.show()
            fig.canvas.draw()
            plt.ylabel('Fitness', fontsize=12)
            plt.xlabel('Time' if self.plot_time_on_x else 'Cycle', fontsize=12)

        print(f"(height, width, depth) = {self.image.shape}",
              end='\n' if sum(self.original_size) == sum(self.image.shape[0:2]) else f" [resized from {' by '.join(map(str, self.original_size))}]\n")

        if not self.fitness_func:
            self.fitness_func = FitnessCalculator(self.image).ssd
            self.partial_fitness_func = FitnessCalculator(self.image).partial_ssd

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
        should_plot = lambda cycle: False if not self.plot_cycle else cycle % self.plot_cycle == 0

        if not self.random_hard_mutation_prob: self.random_hard_mutation_prob = 0.0
        should_hard_mutate = lambda fitness: \
            np.random.random() < self.random_hard_mutation_prob or (False if not self.hard_mutation_fitness_limit else fitness >= self.hard_mutation_fitness_limit)
        
        unimproved_cycles = 0
        prev_best_fitness = None

        try:
            while should_cycle(self.cycle):
                population.iterate(self.fitness_func, 
                                   hard_mutation=should_hard_mutate(population.best_fitness),
                                   mutation_rate=self.mutation_rate or 1.0,
                                   crossover_rate=self.crossover_rate or 0.0,
                                   selection_strategy=self.selection_strategy or 'truncation',
                                   crossover_strategy=self.crossover_strategy or 'single_point',
                                   substitution_method=self.substitution_method or 'tournament')

                self.cycle += 1
                unimproved_cycles = 0 if population.best_fitness != prev_best_fitness else unimproved_cycles + 1
                prev_best_fitness = population.best_fitness
                if self.max_unimproved_cycles is not None and unimproved_cycles > self.max_unimproved_cycles:
                    print(f"\nHalting, {unimproved_cycles} consecutive unimproved cycles")
                    break

                curr_duration = time() - start_time
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
                    fitnesses = list(map(lambda pack: pack.fitness, population.packs))
                    curr_avg_fitness = statistics.mean(fitnesses)
                    curr_worst_fitness = max(fitnesses)
                    
                    if self.cycle == 1:
                        plt.ylim(top=1.1*curr_worst_fitness)
                    plt.ylim(bottom=0.9*population.best_fitness)

                    plot_avg.set_ydata(np.append(plot_avg.get_ydata(), curr_avg_fitness))
                    plot_best.set_ydata(np.append(plot_best.get_ydata(), population.best_fitness))
                    plot_worst.set_ydata(np.append(plot_worst.get_ydata(), curr_worst_fitness))

                    plot_avg.set_xdata(np.append(plot_avg.get_xdata(), curr_duration if self.plot_time_on_x else self.cycle))
                    plot_best.set_xdata(np.append(plot_best.get_xdata(), curr_duration if self.plot_time_on_x else self.cycle)) 
                    plot_worst.set_xdata(np.append(plot_worst.get_xdata(), curr_duration if self.plot_time_on_x else self.cycle)) 
                    
                    plt.xlim([0, curr_duration if self.plot_time_on_x else self.cycle])

                    fig.canvas.draw() 

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
            
            if self.save_plot_path:
                save_path = os.path.join(self.save_plot_path, f"{self.save_plot_prefix}_{'time' if self.x_time else 'cycle'}_{self.cycle}.png")
                plt.savefig(save_path, dpi=256, bbox_inches='tight')
                print(f"\nPlot saved at {save_path}")

            if self.population_size > 1 and self.save_all_path:
                save_path = os.path.join(self.save_all_path, f"{self.save_all_final_prefix}{self.cycle}.png")
                population.save_all(save_path)
                print(f"\nFinal population saved at {save_path}")

            if self.save_dna_path and population.best_fitness < self.save_dna_min_fitness:
                save_path = os.path.join(self.save_dna_path, f"{self.save_dna_prefix}{self.cycle}.pkl")
                with open(save_path, "wb+") as f: # binary file
                    f.write(population.best_dna)
                print(f"\nBest solution's DNA saved at {save_path}")  