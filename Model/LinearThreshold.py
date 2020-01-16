from graph_tool.all import *
from typing import Callable
from .Model import Model
from numpy.random import ranf, randint

class IndependantCascade(Model):

    def __init__(self, graph: Graph = None, heuristic: Callable = None, seed_set_size: int = None) -> None:
        super(IndependantCascade, self).__init__(graph, heuristic, seed_set_size)

        # Default values for generating default graphs
        self._size = 1000
        self._density = 0.3

    def _simulate(self) -> Graph:
        g = self.graph

        # Go through all of the inactive nodes.
        # activate them if needed
        # if none are activated then stop

        # t = 1
        # g_ = GraphView(g, vfilt=lambda v: g.vertex_properties["active"][v] == 0)
        # while g_.num_vertices() != 0:
        #     for n in g_.vertices():
        #         # Go through the neighboors
        #         v = g.vertex(n)
        #         for e_neighbour, n_neighbour in zip(v.out_edges(), v.out_neighbors()):
        #             # Check if the node is activated and make sure not to give it a second life
        #             if g.edge_properties["weight"][e_neighbour] > ranf(1) \
        #                     and g.vertex_properties["active"][n_neighbour] == 0:
        #                 g.vertex_properties["active"][n_neighbour] = t + 1
        #     t += 1
        #     g_ = GraphView(g, vfilt=lambda v: g.vertex_properties["active"][v] == 0)
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