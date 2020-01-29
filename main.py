from graph_tool.all import *
from numpy.random import ranf, randint, randn
from Model.Model import Model
from Model.IndependantCascade import IndependantCascade
from Heuristic.Heuristic import Heuristic
from Heuristic.Random import Random
from Heuristic.DegreePriority import DegreePriority
from TestSuite.TestSuite import TestSuite
import json

import plotly.graph_objects as go


# TEMP
size = 15000
density = int(size**2 * 0.00027)
propagation = 0.01

def gen_graph(size, density):
    # Create the graph
    g = Graph()

    # Add the vertexes
    g.add_vertex(size)

    # insert some random links
    for s, t in zip(randint(0, size, density), randint(0, size, density)):
        e = g.add_edge(g.vertex(s), g.vertex(t))

    weight = g.new_edge_property("double", vals=[propagation for i in range(density)])
    g.edge_properties["weight"] = weight

    active = g.new_vertex_property("int")
    g.vertex_properties["active"] = active

    return g

def stats(model: Model, heuristic: Heuristic, graph: Graph, seed_set_size: int, R: int) -> None:
    results = list()
    # Run the simulation R times
    for i in range(R):
        result = model(graph.copy(), heuristic, seed_set_size)
        result.simulate()
        results.append(result.graph)
    # Stats !
    total = list()
    num_infected = 0
    per_infected = 0
    for r in results:
        g = GraphView(r, vfilt=lambda v: r.vertex_properties["active"][v] > 0)
        infected_number = len(g.get_vertices())
        # print(len(g.get_vertices()), len(r.get_vertices()))
        infected_percentage = 100 * infected_number/(len(r.get_vertices()))
        total.append({"number_of_infected": infected_number, "percentage_of_infected": infected_percentage})
        num_infected += infected_number
        per_infected += infected_percentage
    print(total)
    print(num_infected/R)
    print(per_infected/R)




# stats(IndependantCascade, Random, gen_graph(size, density), 20, 50)
TestSuite()
# with open("results.json", "r") as fp:
#     data = json.load(fp)
#     print(data)
# graph_draw(g, output_size=(1000, 1000), output="graph.png")
