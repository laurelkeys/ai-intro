import os
from time import time

import numpy as np
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
        # NOTE self.original_size == (widht, height), while self.image.shape == (height, width, depth)

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

    def show_at(self, show_cycle=1, show_all=False):
        self.show_cycle = show_cycle
        self.show_all = show_all
        return self

    def plot_at(self, plot_cycle=1, x_time=False):
        self.plot_cycle = plot_cycle
        self.x_time = x_time 
        return self

    def reproduce_at(self, reproduction_cycle=100):
        self.reproduction_cycle = reproduction_cycle
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

    def run(self, use_partial_fitness=True, use_image_colors=True):
        height, width, *_ = self.image.shape

        if self.plot_cycle != None: 
            plot_best, *_ = plt.plot([], [])
            plot_worst, *_ = plt.plot([], [])
            plot_best.set_color("blue")
            plot_worst.set_color("red")
            fig = plt.gcf()
            fig.show()
            fig.canvas.draw()
            plt.ylabel('Fitness', fontsize=12)
            if self.x_time == True:
                plt.xlabel('Time', fontsize=12)
            else:
                plt.xlabel('Fitness', fontsize=12)


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
        should_reproduce = lambda cycle: False if not self.reproduction_cycle else cycle % self.reproduction_cycle == 0

        try:
            while should_cycle(self.cycle):
                if use_partial_fitness:
                    population.cycle(self.fitness_func, self.partial_fitness_func, prophase=should_reproduce(self.cycle))
                else:
                    population.cycle(self.fitness_func, prophase=should_reproduce(self.cycle))

                self.cycle += 1
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
                    if self.cycle == 1:
                            plt.ylim([0, population.worst_fitness + population.worst_fitness/20])
                    plot_best.set_ydata(np.append(plot_best.get_ydata(), population.best_fitness))
                    plot_worst.set_ydata(np.append(plot_worst.get_ydata(), population.worst_fitness))  
                    if self.x_time == False: 
                        plot_best.set_xdata(np.append(plot_best.get_xdata(), self.cycle)) 
                        plot_worst.set_xdata(np.append(plot_worst.get_xdata(), self.cycle)) 
                        plt.xlim([0, self.cycle]) 
                    else:
                        plot_best.set_xdata(np.append(plot_best.get_xdata(), time() - start_time)) 
                        plot_worst.set_xdata(np.append(plot_worst.get_xdata(), time() - start_time)) 
                        plt.xlim([0, time() - start_time]) 
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
            
            if self.plot_cycle != None:
                save_path = os.path.join(self.save_best_path, f"{self.cycle}_plot.png")
                plt.savefig(save_path)
                print(f"\nplot saved at {save_path}")

            if self.population_size > 1 and self.save_all_path:
                save_path = os.path.join(self.save_all_path, f"{self.save_all_final_prefix}{self.cycle}.png")
                population.save_all(save_path)
                print(f"\nFinal population saved at {save_path}")

            if self.save_dna_path and population.best_fitness < self.save_dna_min_fitness:
                save_path = os.path.join(self.save_dna_path, f"{self.save_dna_prefix}{self.cycle}.pkl")
                with open(save_path, "wb+") as f: # binary file
                    f.write(population.best_dna)
                print(f"\nBest solution's DNA saved at {save_path}")  