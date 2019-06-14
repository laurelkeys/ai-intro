from os import path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

show = True
save = False
annotate = False
behaviors = [('cohesion', 'position'), ('separation', 'position'), ('alignment', 'direction')]

for behavior, y_axis in behaviors:
    raw = pd.read_csv(path.join('heatmap', f'{behavior}.csv'))
    matrix = raw.pivot(y_axis, "distance", "headingChange")

    fig = plt.figure(figsize=(7,6))
    r = sns.heatmap(matrix, cmap='BuPu', annot=annotate, fmt=".1f")
    r.set_title(f"{behavior.title()}'s defuzzified headingChange output")
    plt.tight_layout()
    if (show): plt.show()
    if (save): fig.savefig(f'{behavior}.png')
