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
    raw = pd.read_csv(path.join('heatmap', f'{behavior}-10-10.csv'))
    matrix = raw.pivot(y_axis, "distance", "headingChange")

    fig = plt.figure(figsize=(7,6))
    r = sns.heatmap(matrix, cmap='BuPu', annot=annotate, fmt=".1f")
    r.set_title(f"{behavior.title()}'s defuzzified headingChange output")
    plt.tight_layout()
    if (show): plt.show()
    if (save): fig.savefig(f'{behavior}.png')

# for method in ['cog', 'coa', 'lm', 'rm', 'mm']:
#     cohesion_raw = pd.read_csv(f'heatmap\\cohesion_{method}.csv')
#     cohesion_matrix = cohesion_raw.pivot("position", "distance", "headingChange")

#     fig = plt.figure(figsize=(7,6))
#     r = sns.heatmap(cohesion_matrix, cmap='BuPu', linewidths=.5, annot=True, fmt=".1f")
#     r.set_title(f"Cohesion's {method.upper()} defuzzified headingChange output")
#     plt.tight_layout()