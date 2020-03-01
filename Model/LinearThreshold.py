from graph_tool.all import *
from typing import Callable
from .Model import Model
from numpy.random import ranf, randint
from numpy import sum, vectorize


class LinearThreshold(Model):

    def __init__(self, graph: Graph = None, heuristic: Callable = None, seed_set_size: int = None) -> None:
        super(LinearThreshold, self).__init__(graph, heuristic, seed_set_size)

        # Default values for generating default graphs
        self._size = 1000
        self._density = 0.3

    def _simulate(self) -> Graph:
        g = self.graph
        t = 1
        g_ = GraphView(g, vfilt=lambda v: g.vertex_properties["active"][v] == t)
        while g_.num_vertices() != 0:
            # print(g_.num_vertices())
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
                    test = vectorize(lambda x: g.edge_properties["weight"][g.edge(n_neighbour, x)])
                    activation_force = sum(test(active_neighbours))

                    if g.vertex_properties["threshold"][n_neighbour] < activation_force:
                        g.vertex_properties["active"][n_neighbour] = t + 1
            t += 1
            g_ = GraphView(g, vfilt=lambda v: g.vertex_properties["active"][v] == t)
        # print("END")
        return g

    def _generate_default_graph(self) -> None:
        size = self._size
        density = self._density
        # Create the graph
        g = Graph()

        # Add the vertexes
        g.add_vertex(size)

        # go through each node and its in-edges and give them a combined weight of less than 1

        # insert some random links
        for s, t in zip(randint(0, size, density), randint(0, size, density)):
            e = g.add_edge(g.vertex(s), g.vertex(t))

        weight = g.new_edge_property("double")
        g.edge_properties["weight"] = weight

        threshold = g.new_vertex_property("double", vals=ranf(size))
        g.vertex_properties["threshold"] = threshold

        active = g.new_vertex_property("int")
        g.vertex_properties["active"] = active

        self.graph = g