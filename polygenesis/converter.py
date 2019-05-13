# NOTE: The Canvas class has been developed by Jon Carr (https://github.com/jwcarr/svg-polygons)

import os
import pickle

class Canvas:

    canvas = ''
    shape_count = 0

    def __init__(self, width=500, height=500):
        self.width = width
        self.height = height

    def polygon(self, shape, border_colour=None, fill_colour=None, opacity=1.0):
        canvas = "\n  <g id='shape%s'>" % self.shape_count
        points = [(str(vertex[0]) + "," + str(vertex[1])) for vertex in shape]
        canvas += "\n    <polygon points='" + (" ".join(points)) + "' style='fill:%s; stroke:%s; fill-opacity:%s; stroke-opacity:%s; stroke-width:3; stroke-linejoin:miter;' />" % (fill_colour, border_colour, opacity, opacity)
        canvas += "\n  </g>\n"
        self.canvas += canvas
        self.shape_count += 1

    def __add_header(self):
        return "<svg xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#' xmlns:svg='http://www.w3.org/2000/svg' xmlns='http://www.w3.org/2000/svg' version='1.1' width='" + str(self.width) + "' height='" + str(self.height) + "'>\n"

    def __add_canvas(self):
        return self.canvas + "\n"

    def __add_footer(self):
        return "</svg>"

    def save(self, filename='drawing'):
        canvas = self.__add_header()
        canvas += self.__add_canvas()
        canvas += self.__add_footer()
        with open(filename + '.svg', 'w') as f:
            f.write(canvas)
        print("Image saved at %s.svg" % filename)

def hex_string(rgb_list):
    return "#%0.2X%0.2X%0.2X" % (rgb_list[0], rgb_list[1], rgb_list[2])

def convert_and_save(dna_path, save_path, prefix=None):
    with open(dna_path, 'rb') as f:
        dna_obj = pickle.load(f)

    width, height, bg_color = dna_obj['width'], dna_obj['height'], dna_obj['bg_color']
    drawing = Canvas(width, height)
    drawing.polygon(shape=[(0, 0), (width, 0), (width, height), (0, height)], fill_colour=hex_string(bg_color), opacity=1.0)

    for color, polygon in zip(dna_obj['colors'], dna_obj['polygons']):
        polygon = [(x, y) for (x, y) in zip(polygon[0::2], polygon[1::2])] # [x, y, x, y, ...] -> [(x, y), (x, y), ...]
        drawing.polygon(shape=polygon, fill_colour=hex_string(color), opacity=color[3] / 255)

    if not prefix: prefix = os.path.splitext(os.path.basename(os.path.normpath(dna_path)))[0]
    drawing.save(filename=os.path.join(save_path, prefix))

# e.g.
# convert_and_save(os.path.join("generated", "dna", "dna_ml_400000.pkl"), os.path.join("generated", "vector"))