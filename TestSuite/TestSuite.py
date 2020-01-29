import json
from graph_tool.all import *
from numpy.random import ranf, randint
from Model.Model import Model
from Model.IndependantCascade import IndependantCascade
from Heuristic.Heuristic import Heuristic
from Heuristic.Random import Random
from Heuristic.DegreePriority import DegreePriority
from numpy.random import normal
from numpy import divide, zeros
from typing import List
import plotly.graph_objects as go
from itertools import zip_longest
from time import time


class TestSuite:

    def __init__(self, params = "parameters.json"):
        try:
            with open(params,"r") as fp:
                parameters = json.load(fp)
        except Exception as e:
            print("error parsing the parameters: \n" + str(e))
            exit(-1)

        # create a map with models, one with heuristics
        # whenever there is an array create a job with each of the values (only support one array at a time to start with)
        # Go through each job. and store the results
        influence_average = []
        for seedsetsize in parameters["SeedSetSize"]:
            influence_average_num = 0
            for NumGraphs in range(parameters["NumGraphs"]):
                graph = self.gen_graph(parameters["Graphs"]["Cardinality"], parameters["Models"]["IC"]["Propagation"])
                # Store the results of R simulation on a randomly generated graph
                results_on_r = []
                for i in range(parameters["R"]):
                    result = IndependantCascade(graph.copy(), DegreePriority, seedsetsize)
                    result.simulate()
                    results_on_r.append(result.graph)
                influence_average_num += self.R_stats(results_on_r)
            print(str(seedsetsize) + ": " + str(influence_average_num/parameters["NumGraphs"]))
            influence_average.append(influence_average_num/parameters["NumGraphs"])
        self.store(influence_average, "Influence_average")

    def gen_graph(self, size, propagation):

        g = random_graph(size, lambda: normal(10, 2), directed=False)
        weight = g.new_edge_property("double", vals=[propagation for i in range(len(g.get_edges()))])
        g.edge_properties["weight"] = weight

        active = g.new_vertex_property("int")
        g.vertex_properties["active"] = active

        return g

    def R_stats(self, gs: List[Graph]) -> None:
        # average number of the influence
        # draw the graph
        xs = zeros(1)
        for g in gs:
            x = vertex_hist(g, g.vertex_properties["active"], [0, 1])
            xs = [x+y for x, y in zip_longest(xs, x[0], fillvalue=0)]
        # The average for this graph on R
        xs = divide(xs, len(gs))
        # self.store(xs, "R_stats")
        # Return the number of influenced nodes
        return sum(xs[1:])

    def store(self, data, name):
        json_data = json.dumps(list(data))
        with open(name + str(time()) + ".json", "w") as f:
            json.dump(json_data, f)
