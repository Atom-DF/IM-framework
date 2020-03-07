from .Graph import Graph_Blank
from numpy.random import normal
from graph_tool.all import *


class RandomGraph(Graph_Blank):
    def __init__(self, cardinality: int, degree_sampler=lambda: normal(6, 1)):
        super(RandomGraph, self).__init__()
        self.cardinality = cardinality
        self.degree_sampler = degree_sampler

    def generate(self) -> Graph:
        g = random_graph(self.cardinality, self.degree_sampler, directed=False)

        active = g.new_vertex_property("int")
        g.vertex_properties["active"] = active
        return g
