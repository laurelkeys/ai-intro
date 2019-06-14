import json
import matplotlib.pyplot as plt
import numpy as np

with open("maxavg.json","r") as maxavg_f, open("maxmax.json","r") as maxmax_f, open("maxmin.json","r") as maxmin_f, \
     open("minavg.json","r") as minavg_f, open("minmax.json","r") as minmax_f, open("minmin.json","r") as minmin_f:

    maxavg = json.loads(maxavg_f.read())
    maxmax = json.loads(maxmax_f.read())
    maxmin = json.loads(maxmin_f.read())

    minavg = json.loads(minavg_f.read())
    minmax = json.loads(minmax_f.read())
    minmin = json.loads(minmin_f.read())

    x = list(range(0, len(minmin)))
    fig, ax = plt.subplots(1, 1, sharex=True)
    ax.set_xlim(0, 1000)

    ax.set_title('Inter-agent distance')
    ax.plot(x, minavg, color=(0.12, 0.47, 0.7, 1))
    ax.plot(x, maxavg, color=(0, 0.5, 0, 1))
    ax.fill_between(x, minmax, maxmax,
                    facecolor='lightgreen', interpolate=True, alpha=0.5)
    ax.fill_between(x, minmin, maxmin,
                    facecolor='lightblue', interpolate=True, alpha=0.5)

    plt.show()