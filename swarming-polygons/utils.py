import numpy as np

class FitnessCalculator:
    def __init__(self, original_image):
        self.original_image = original_image
    
    def fitness_sad(self, pack_image):
        return np.abs(np.subtract(self.original_image, pack_image, dtype=np.int16), dtype=np.int16).sum() # sum absolute difference

    def fitness_ssd(self, pack_image):
        return np.square(np.subtract(self.original_image, pack_image, dtype=np.int16), dtype=np.int64).sum() # sum square difference

    def partial_fitness_ssd(self, pack_image, vertices, mutant_vertices):
        min_y = min(min(vertices[1::2]), min(mutant_vertices[1::2]))
        max_y = max(max(vertices[1::2]), max(mutant_vertices[1::2]))
        min_x = min(min(vertices[0::2]), min(mutant_vertices[0::2]))
        max_x = max(max(vertices[0::2]), max(mutant_vertices[0::2]))
        return np.square(np.subtract(self.original_image[min_y:max_y, min_x:max_x, :], pack_image[min_y:max_y, min_x:max_x, :], dtype=np.int16), dtype=np.int32).sum()

def avg_color(image):
    size = image.shape[0] * image.shape[1] # image.shape == (height, width, depth)
    r_sum = image[:, :, 0].sum()
    g_sum = image[:, :, 1].sum()
    b_sum = image[:, :, 2].sum()
    return (int(r_sum / size), int(g_sum / size), int(b_sum / size))

def vertices_color_avg(polygon, vertices_count, image, alpha=128):
    vertices_color_avg = np.array([0, 0, 0, alpha], dtype=np.uint) # [R, G, B, Alpha]
    for j in range(vertices_count):
        x, y = polygon[(2*j) : (2*j) + 2]
        vertices_color_avg[0:3] += image[y, x, :]
    vertices_color_avg //= vertices_count
    return vertices_color_avg

def vertices_color_mid(polygon, vertices_count, image, alpha=128):
    vertices_color_mid = np.array([0, 0, 0, alpha], dtype=np.uint) # [R, G, B, Alpha]
    min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
    for j in range(vertices_count):
        x, y = polygon[(2*j) : (2*j) + 2]
        if x < min_x: min_x = x
        if x > max_x: max_x = x
        if y < min_y: min_y = y
        if y > max_y: max_y = y
    vertices_color_mid[0:3] = image[(min_y + max_y) // 2, (min_x + max_x) // 2, :]
    return vertices_color_mid