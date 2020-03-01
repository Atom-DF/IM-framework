from graph_tool.all import *
from .Heuristic import Heuristic
from numpy.random import ranf, randint, choice
from timeit import default_timer as timer


class Random(Heuristic):

    @staticmethod
    def generate(g: Graph, size: int):
        s = []
        for v in choice(range(len(list(g.vertices()))), size):
            s.append(g.vertex(v, use_index=False))
        return s


