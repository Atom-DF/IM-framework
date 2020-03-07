from graph_tool.all import *
from typing import Callable
from .Model import Model
from numpy.random import ranf, randint
from numpy import sum, vectorize


class LinearThreshold(Model):

    def __init__(self, graph: Graph = None, seed_set = None) -> None:
        super(LinearThreshold, self).__init__(graph, seed_set)

    def _simulate(self) -> Graph:
        g = self.graph
        t = 1
        g_ = GraphView(g, vfilt=lambda v: g.vertex_properties["active"][v] == t)
        while g_.num_vertices() != 0:
            for n in g_.vertices():
                # Go through the neighboors
                v = g.vertex(n)
                for n_neighbour in v.out_neighbors():
                    # dont calculate anything if its activated already
                    if g.vertex_properties["active"][n_neighbour] != 0:
                        continue
                    # sum the weight of all its activated neighboors
                    # check if you need to activate it
                    active_neighbours = g_.get_out_neighbors(n_neighbour, [g.vertex_properties["active"]])[:, 0]
                    f = vectorize(lambda x: g.edge_properties["weight"][g.edge(n_neighbour, x)])
                    activation_force = sum(f(active_neighbours))

                    if g.vertex_properties["threshold"][n_neighbour] < activation_force:
                        g.vertex_properties["active"][n_neighbour] = t + 1
            t += 1
            g_ = GraphView(g, vfilt=lambda v: g.vertex_properties["active"][v] == t)
        return g

    @staticmethod
    def set_up(g, params) -> None:
        weight = g.new_edge_property("double")
        weight.set_value(1.0)
        g.edge_properties["weight"] = weight

        threshold = g.new_vertex_property("double", vals=[params["Threshold"]] * len(g.get_vertices()))
        g.vertex_properties["threshold"] = threshold

        for v in g.vertices():
            for e in v.out_edges():
                g.edge_properties["weight"][e] = 1 / v.out_degree() if 1 / v.out_degree() < g.edge_properties["weight"][e] else g.edge_properties["weight"][e]
        return g
