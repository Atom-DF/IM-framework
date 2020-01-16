from graph_tool.all import *
from .Heuristic import Heuristic
from numpy.random import ranf, randint, choice

class Random(Heuristic):

    @staticmethod
    def generate(g: Graph, size: int):
        for v in choice(range(len(list(g.vertices()))), size):
            g.vertex_properties["active"][g.vertex(v)] = 1
        return g


