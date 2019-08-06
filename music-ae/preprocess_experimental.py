from functools import reduce

import numpy as np

# FIXME TODO improve functions performance/readability after testing

'''
    segment_t(sequence, seg_size) is equal to preprocess.segment
    with overlap_size = seg_size/2, delta = seg_size/2
'''
def segment_t(sequence, seg_size):
    assert(seg_size % 2 == 0) # TODO treat odd cases
    return [sequence[d : d + seg_size] for d in range(0, len(sequence) - seg_size + 1, seg_size / 2)]


'''
    adds a segmented wave modulated by a triangular function
'''
def add_overlap_t(segmented, seg_size):
    assert(seg_size % 2 == 0) # TODO treat odd cases
    half_seg_size = seg_size // 2

    # assert(len(segmented[0]) == seg_size)
    result_wave = np.array(trianglify(segmented[0], up=False))

    for i in range(1, len(segmented) - 1):
        # assert(len(segmented[i]) == seg_size)
        t = trianglify(segmented[i])
        result_wave[-half_seg_size:] += t[:half_seg_size]
        result_wave = np.append(result_wave, t[half_seg_size:])

    # assert(len(segmented[-1]) == seg_size)
    t = trianglify(segmented[-1], down=False)
    result_wave[-half_seg_size:] += t[:half_seg_size]
    result_wave = np.append(result_wave, t[half_seg_size:])
    return result_wave


'''
    multiplies a wave segment by a triangular function with height = 1 and width = seg_size
'''
def trianglify(segment, up=True, down=True):
    assert(len(segment) % 2 == 0) # TODO treat odd cases
    half_seg_size = len(segment) // 2
    # dx = 1
    dy = 1 / half_seg_size # 2 / len(segment)

    ascent = np.linspace(dy, 1-dy, half_seg_size) # np.linspace(0, 1, half_seg_size)
    descent = np.ones(ascent.shape) - ascent

    # 1st half, x in [0, w/2): f(x) = x / (w/2)
    if up: segment[:half_seg_size] *= ascent

    # 2nd half, x in [w/2, w]: f(x) = 2 - x / (w/2)
    if down: segment[half_seg_size:] *= descent

    return segment