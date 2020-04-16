from graph_tool.all import *
from .Heuristic import Heuristic
from timeit import default_timer as timer
from numpy.random import ranf, randint, choice


class DegreeDiscount(Heuristic):

    @staticmethod
    def generate(g_: Graph, size: int):
        ddv = g_.new_vertex_property("float", vals=g_.get_out_degrees(g_.get_vertices()))
        g_.vertex_properties["ddv"] = ddv

        tv = g_.new_vertex_property("int", vals=[0]*len(g_.get_vertices()))
        g_.vertex_properties["tv"] = tv


        s = []
        for i in range(size):
            vertices = g_.get_vertices()
            degrees = zip([g_.vertex_properties["ddv"][vi] for vi in vertices], vertices)
            temp = max(degrees, key=lambda vertex: vertex[0])
            s.append(temp[1])
            node = g_.vertex(temp[1])
            for j in g_.get_out_neighbors(node):
                g_.vertex_properties["tv"][j] = g_.vertex_properties["tv"][j] + 1
                g_.vertex_properties["ddv"][j] = g_.vertex_properties["ddv"][j] - 2*g_.vertex_properties["tv"][j] \
                                                 - (node.out_degree() - g_.vertex_properties["tv"][j])\
                                                 * g_.vertex_properties["tv"][j] \
                                                 * g_.edge_properties["weight"][g_.edge(j, node)]
            g_ = GraphView(g_, vfilt=lambda v: v not in s)
        return s
