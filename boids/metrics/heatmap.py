from IPython.core.display import HTML
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

annotate = False
behaviors = [('cohesion', 'position'), ('separation', 'position'), ('alignment', 'direction')]

for behavior, y_axis in behaviors:
    raw = pd.read_csv(f'{behavior}.csv')
    matrix = raw.pivot(y_axis, "distance", "headingChange")

    fig = plt.figure(figsize=(7,6))
    r = sns.heatmap(matrix, cmap='BuPu', linewidths=.5, annot=annotate, fmt=".1f")
    r.set_title(f"{behavior.title()}'s defuzzified headingChange output")
    plt.tight_layout()
    plt.show()