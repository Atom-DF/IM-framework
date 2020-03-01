from graph_tool.all import *
from .Heuristic import Heuristic
from timeit import default_timer as timer
from numpy.random import ranf, randint, choice


class DegreePriority(Heuristic):

    @staticmethod
    def generate(g: Graph, size: int):
        vertices = g.get_vertices()
        degrees = zip(g.get_out_degrees(vertices), vertices)
        sorted_list = sorted(degrees, key=lambda vertex: vertex[0])
        return [sorted_list[-i][1] for i in range(1, size+1)]
