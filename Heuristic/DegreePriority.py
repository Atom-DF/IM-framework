from graph_tool.all import *
from .Heuristic import Heuristic
from numpy.random import ranf, randint, choice

class DegreePriority(Heuristic):

    @staticmethod
    def generate(g: Graph, size: int):
        vertices = g.get_vertices()
        test = zip(g.get_out_degrees(vertices), vertices)
        sorted_list = sorted(test, key= lambda vertex: vertex[0])
        for i in range(size):
            g.vertex_properties["active"][g.vertex(sorted_list[i][1])] = 1
        return g
