from IPython.core.display import HTML
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

cohesion_raw = pd.read_csv('cohesion.csv')
cohesion_raw["position"] = pd.Categorical(cohesion_raw["position"], cohesion_raw.position.unique())
cohesion_raw.head()
cohesion_matrix = cohesion_raw.pivot("position", "distance", "headingChange")

fig = plt.figure(figsize=(7,6))
r = sns.heatmap(cohesion_matrix, cmap='BuPu', linewidths=.5, annot=True, fmt=".1f")
r.set_title("Cohesion's heatmap of the defuzzified headingChange output")
plt.tight_layout()
plt.show()

separation_raw = pd.read_csv('separation.csv')
separation_raw["position"] = pd.Categorical(separation_raw["position"], separation_raw.position.unique())
separation_raw.head()
separation_matrix = separation_raw.pivot("position", "distance", "headingChange")

fig = plt.figure(figsize=(7,6))
r = sns.heatmap(separation_matrix, cmap='BuPu', linewidths=.5, annot=True, fmt=".1f")
r.set_title("Separation's heatmap of the defuzzified headingChange output")
plt.tight_layout()
plt.show()

alignment_raw = pd.read_csv('alignment.csv')
alignment_raw["direction"] = pd.Categorical(alignment_raw["direction"], alignment_raw.direction.unique())
alignment_raw.head()
alignment_matrix = alignment_raw.pivot("direction", "distance", "headingChange")

fig = plt.figure(figsize=(7,6))
r = sns.heatmap(alignment_matrix, cmap='BuPu', linewidths=.5, annot=True, fmt=".1f")
r.set_title("Alignment's heatmap of the defuzzified headingChange output")
plt.tight_layout()
plt.show()