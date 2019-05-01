import numpy as np

class FitnessCalculator:
    def __init__(self, original_image):
        self.original_image = original_image
    
    def fitness_sad(self, pack_image):
        return np.abs(np.subtract(self.original_image, pack_image, dtype=np.int16), dtype=np.int16).sum() # sum absolute difference

    def fitness_ssd(self, pack_image):
        # FIXME since the image's values are in [0, 255], the square might be doable with np.uint16
        return np.square(np.subtract(self.original_image, pack_image, dtype=np.int16), dtype=np.int32).sum() # sum square difference

def avg_color(image):
    size = image.shape[0] * image.shape[1] # image.shape == (height, width, depth)
    r_sum = image[:, :, 0].sum()
    g_sum = image[:, :, 1].sum()
    b_sum = image[:, :, 2].sum()
    return (int(r_sum / size), int(g_sum / size), int(b_sum / size))