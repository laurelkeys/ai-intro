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
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True)

    ax1.plot(x, maxavg, color='black')
    ax1.set_title('MAX')
    # Test support for masked arrays.
    ax1.fill_between(x, maxavg, maxmax,
                    facecolor='green', interpolate=True , alpha=0.5)
    ax1.fill_between(x, maxavg, minmax,
                    facecolor='lightgreen', interpolate=True, alpha=0.5) 
                    

    ax2.plot(x, minavg, color='black')
    ax2.set_title('MIN')
    ax2.fill_between(x, minavg, maxmin,
                    facecolor='blue', interpolate=True, alpha=0.5)
    ax2.fill_between(x, minavg, minmin,
                    facecolor='lightblue', interpolate=True, alpha=0.5)
    # ax1.fill_between(x, y1, y2, where=y2 <= y1,
    #                  facecolor='red', interpolate=True)
    # ax1.set_title('Now regions with y2>1 are masked')

    ax3.set_title('Inter-agent distance')
    ax3.plot(x, minavg, color=(0.12, 0.47, 0.7, 1))
    ax3.plot(x, maxavg, color=(0, 0.5, 0, 1))
    ax3.fill_between(x, minmin, maxmin,
                    facecolor=(0.7, 0.8, 0.9), interpolate=True, alpha=0.5)
    ax3.fill_between(x, minmax, maxmax,
                    facecolor=(0.7, 0.8, 0.7), interpolate=True, alpha=0.5)

    plt.show()