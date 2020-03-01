from graph_tool.all import *
from .Heuristic import Heuristic
from timeit import default_timer as timer
from numpy.random import ranf, randint, choice


class SingleDiscount(Heuristic):

    @staticmethod
    def generate(g: Graph, size: int):
        g_ = g
        s = []
        for i in range(size):
            vertices = g_.get_vertices()
            degrees = zip(g_.get_out_degrees(vertices), vertices)
            temp = max(degrees, key=lambda vertex: vertex[0])
            s.append(temp[1])
            g_ = GraphView(g, vfilt=lambda v: v not in s)
        return s
