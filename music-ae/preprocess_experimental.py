import numpy as np
import matplotlib.pyplot as pyplot

def trianglify(segment, up=True, down=True, start_from_zero=False):
    assert(len(segment) % 2 == 0)
    half_seg_size = len(segment) // 2
    dy = 0 if start_from_zero else 1 / half_seg_size

    ascent = np.linspace(dy, 1-dy, half_seg_size) # np.linspace(0, 1, half_seg_size)
    descent = np.ones(ascent.shape) - ascent      # np.linspace(1, 0, half_seg_size)
    segment_t = np.array(segment, dtype=float)

    if up:   segment_t[:half_seg_size] *= ascent  # 1st half, x in [0, w/2): f(x) = x / (w/2)

    if down: segment_t[half_seg_size:] *= descent # 2nd half, x in [w/2, w]: f(x) = 2 - x / (w/2)

    return segment_t

###############################################################

def print_arr(arr, arr_name="arr", only_shape=False):
    try:
        print(f"{arr_name}.shape={arr.shape}")
        if not only_shape: print(f"{arr_name}={arr}\n")
    except:
        np_arr = np.array(arr)
        print(f"*{arr_name}.shape={np_arr.shape}")
        if not only_shape: print(f"*{arr_name}={np_arr}\n")

###############################################################

import sys
from scipy.io import wavfile

src_fname = 'link.wav' if len(sys.argv) < 2 else sys.argv[1]
dst_fname = 'link_procd.wav' if len(sys.argv) < 3 else sys.argv[2]
sr, wave = wavfile.read(src_fname)
print(f"src_fname={src_fname}\ndst_fname={dst_fname}\n")
print(f"sr={sr}, wave.shape={wave.shape}\n")

# [...]
original = np.copy(wave)
seg_size = 32
overlap_size = seg_size // 2

original = original[:, 0] # channel 1
original = original[:len(original)//4]
# original = np.arange(64)
# original = np.ones(64)
print_arr(original, "original")

# [...] -> [[..], ...]
segmented = [original[d:d+seg_size] for d in range(0, len(original) - seg_size + 1, overlap_size)]
print_arr(segmented, "segmented")

# [[..], ...] -> [..]||[..]||... = [.....]
# flattened = [elem for segment in segmented for elem in segment]
# print_arr(flattened, "flattened")

# modulating 'segmented' by a triangular wave
segmented_t = [trianglify(segment, up=i>0, down=i<len(segmented)-1) for i, segment in enumerate(segmented)]
print_arr(segmented_t, "segmented_t")

# adding the modulated overlapping segments of 'segmented_t' to reobtain 'original'
#added_t = np.array(segmented_t[0])
#for i in range(1, len(segmented_t)):
#    segment = segmented_t[i]
#    added_t[-overlap_size:] += segment[:overlap_size]
#    added_t = np.append(added_t, segment[overlap_size:])
added_t = np.zeros(original.shape)
for i in range(0, len(segmented_t)):
    added_t[i * overlap_size : i * overlap_size + seg_size] += segmented_t[i]
print_arr(added_t, "added_t")

equal = all([original[i] == added_t[i] for i in range(0, len(original))])
print(f"equal? {equal}")
if not equal:
    epsilon = 0.00001
    for i in range(0, len(original)):
        if abs(original[i] - added_t[i]) > epsilon:
            print(f"{i}: {original[i]} != {added_t[i]}")

# print(f"\nsaving processed wave to {dst_fname}")
# wavfile.write(dst_fname, rate=sr, data=added_t)