import os
import statistics
import numpy as np
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, xlabel='Cycle', show_plot=True):
        self.show_plot = show_plot
        self.first_cycle = True

        self.plot_worst, *_ = plt.plot([], [], color="red", linestyle=':', linewidth=3, alpha=0.7)
        self.plot_best, *_ = plt.plot([], [], color="blue", linestyle=':', linewidth=3)
        self.plot_avg, *_ = plt.plot([], [], color="orange", alpha=0.7)

        self.fig = plt.gcf() # if show_plot
        if show_plot:
            self.fig.show()

        self.fig.canvas.draw()
        plt.ylabel('Fitness', fontsize=12)
        plt.xlabel(xlabel, fontsize=12)

    
    # the current average and worst fitness are always plotted, the best may either be the current one or the all time best
    def update(self, xdata, fitnesses, all_time_best=None):
        avg_fitness = statistics.mean(fitnesses)
        worst_fitness = max(fitnesses) # NOTE the lower the fitness (= objective function) the better
        best_fitness = all_time_best if all_time_best != None else min(fitnesses)

        if self.first_cycle:
            self.first_cycle = False
            plt.ylim(top=1.05*worst_fitness)
        plt.ylim(bottom=0.95*best_fitness)

        self.plot_worst.set_ydata(np.append(self.plot_worst.get_ydata(), worst_fitness))
        self.plot_best.set_ydata(np.append(self.plot_best.get_ydata(), best_fitness))
        self.plot_avg.set_ydata(np.append(self.plot_avg.get_ydata(), avg_fitness))

        self.plot_worst.set_xdata(np.append(self.plot_worst.get_xdata(), xdata)) 
        self.plot_best.set_xdata(np.append(self.plot_best.get_xdata(), xdata)) 
        self.plot_avg.set_xdata(np.append(self.plot_avg.get_xdata(), xdata))
        
        plt.xlim([0, xdata])

        self.fig.canvas.draw() # if self.show_plot
    
    def save(self, save_path, file_name):
        save_path = os.path.join(save_path, f"{file_name}.png")
        plt.savefig(save_path, dpi=256, bbox_inches='tight')
        print(f"\nPlot saved at {save_path}")

