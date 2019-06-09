import json
import matplotlib.pyplot as plt
import numpy as np

maxavg_f= open("maxavg.json","r")
maxmax_f= open("maxmax.json","r")
maxmin_f= open("maxmin.json","r")
minavg_f= open("minavg.json","r")
minmax_f= open("minmax.json","r")
minmin_f= open("minmin.json","r")

maxavg_c = maxavg_f.read()
maxavg = json.loads(maxavg_c)

maxmax_c = maxmax_f.read()
maxmax = json.loads(maxmax_c)

maxmin_c = maxmin_f.read()
maxmin = json.loads(maxmin_c)

minavg_c = minavg_f.read()
minavg = json.loads(minavg_c)

minmax_c = minmax_f.read()
minmax = json.loads(minmax_c)

minmin_c = minmin_f.read()
minmin = json.loads(minmin_c)


x = list(range(0, len(minmin)))

fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True)
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

plt.show()

maxavg_f.close()
maxmax_f.close()
maxmin_f.close()
minavg_f.close()
minmax_f.close()
minmin_f.close()