from graph_tool.all import *
from typing import Callable
from .Model import Model
from numpy.random import ranf, randint
import functools
from timeit import default_timer as timer


class IndependantCascade(Model):

    def __init__(self, graph: Graph = None, seed_set = None) -> None:
        super(IndependantCascade, self).__init__(graph, seed_set)

    def _simulate(self) -> Graph:
        g = self.graph
        t = 1
        g_ = GraphView(g, vfilt=lambda v: g.vertex_properties["active"][v] == t)
        while g_.num_vertices() != 0:
            for n in g_.vertices():
                # Go through the neighboors
                v = g.vertex(n)
                for e_neighbour, n_neighbour in zip(v.out_edges(), v.out_neighbors()):
                    # Check if the node is activated and make sure not to give it a second life
                    if g.edge_properties["weight"][e_neighbour] > ranf(1) \
                            and g.vertex_properties["active"][n_neighbour] == 0:
                        g.vertex_properties["active"][n_neighbour] = t + 1
            t += 1
            g_ = GraphView(g, vfilt=lambda v: g.vertex_properties["active"][v] == t)
        return g

    @staticmethod
    def set_up(g: Graph, params) -> Graph:
        if not params["Degree_Based"]:
            weight = g.new_edge_property("double", vals=[params["propagation"]] * len(g.get_edges()))
            g.edge_properties["weight"] = weight
        else:
            weight = g.new_edge_property("double")
            weight.set_value(1.0)
            g.edge_properties["weight"] = weight
            for v in g.vertices():
                for e in v.out_edges():
                    g.edge_properties["weight"][e] = 1/v.out_degree() if 1/v.out_degree() < g.edge_properties["weight"][e]\
                        else g.edge_properties["weight"][e]
        return g
