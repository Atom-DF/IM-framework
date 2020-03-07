from .Graph import Graph_Blank
from graph_tool.all import *


class ScaleFreeGraph(Graph_Blank):
    def __init__(self, cardinality, gamma=1, out_degree=4):
        super(ScaleFreeGraph, self).__init__()
        self.cardinality = cardinality
        self.gamma = gamma
        self.out_degree = out_degree

    def generate(self) -> Graph:
        # Barabási–Albert model
        g = price_network(self.cardinality, gamma=self.gamma, m=self.out_degree, directed=False)

        active = g.new_vertex_property("int")
        g.vertex_properties["active"] = active
        return g
