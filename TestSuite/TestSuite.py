import json
from graph_tool.all import *
from numpy.random import ranf, randint
from Model.Model import Model
from Model.IndependantCascade import IndependantCascade
from Model.LinearThreshold import LinearThreshold
from Heuristic.Heuristic import Heuristic
from Heuristic.Random import Random
from Heuristic.DegreePriority import DegreePriority
from Heuristic.SingleDiscount import SingleDiscount
from Heuristic.TIM import TIM
from numpy.random import normal
from numpy import divide, zeros
from typing import List, Union
import plotly.graph_objects as go
from itertools import zip_longest
from time import time


class TestSuite:

    def __init__(self, params="parameters.json"):
        try:
            with open(params, "r") as fp:
                self.parameters = json.load(fp)
        except Exception as e:
            print("error parsing the parameters: \n" + str(e))
            exit(-1)

        # create a map with models, one with heuristics
        # whenever there is an array create a job with each of the values (only support one array at a time to start with)
        # Go through each job. and store the results

        models = {"IC": IndependantCascade, "LT": LinearThreshold}
        heuristics = {"Random": Random, "Degree": DegreePriority, "SingleDiscount": SingleDiscount, "TIM": TIM}

        try:
            model = models[self.parameters["Models"]["Name"]]
        except Exception as e:
            print("Could not find the model in the map: " + self.parameters["Models"]["Name"])
            exit(-1)

        try:
            heuristic = heuristics[self.parameters["Heuristics"]]
        except Exception as e:
            print("Could not find the heuristic in the map:" + self.parameters["Heuristics"])
            exit(-1)


        influence_average = []
        for seedsetsize in self.parameters["SeedSetSize"]:
            influence_average_num = 0
            for NumGraphs in range(self.parameters["NumGraphs"]):
                graph = self.gen_graph()
                # print(graph.num_vertices())
                # print(graph.num_edges())
                # Store the results of R simulation on a randomly generated graph
                results_on_r = []

                # Decide what to show to the heuristic
                graph_copy = self.model_PO(graph.copy())

                # Run the heuristic on it
                seed_set = heuristic.generate(graph_copy, seedsetsize)

                for i in range(self.parameters["R"]):
                    # Run the model on the original graph (all changes made by the heuristic are passed onto graph_copy)
                    result = model(graph_copy, seed_set)
                    # Run the simulation
                    result.simulate()
                    # Some stats
                    results_on_r.append(result.graph)
                influence_average_num += self.R_stats(results_on_r)
            print(str(seedsetsize) + ": " + str(influence_average_num/self.parameters["NumGraphs"]))
            influence_average.append(influence_average_num/self.parameters["NumGraphs"])
        self.store(influence_average, "Influence_average")

    def gen_graph(self):
        # Generate the graph
        if self.parameters["Graphs"]["Generation"] == "R":
            g = random_graph(self.parameters["Graphs"]["Cardinality"], lambda: normal(50, 2), directed=False)

            active = g.new_vertex_property("int")
            g.vertex_properties["active"] = active
        elif self.parameters["Graphs"]["Generation"] == "SF":
            # Barabási–Albert model
            g = price_network(self.parameters["Graphs"]["Cardinality"], gamma=self.parameters["Graphs"]["Gamma"], m=self.parameters["Graphs"]["Out-degree"], directed=False)

            active = g.new_vertex_property("int")
            g.vertex_properties["active"] = active

        else:
            print("error generating graph, graph generation not known")
            exit(-1)

        # Generate Model
        if "IC" == self.parameters["Models"]["Name"]:
            weight = g.new_edge_property("double", vals=[self.parameters["Models"]["Propagation"]]* len(g.get_edges()))
            g.edge_properties["weight"] = weight
        elif "LT" == self.parameters["Models"]["Name"]:
            weight = g.new_edge_property("double", vals=ranf(len(g.get_edges())))
            g.edge_properties["weight"] = weight

            threshold = g.new_vertex_property("double", vals=[self.parameters["Models"]["Threshold"]]* len(g.get_vertices()))
            g.vertex_properties["threshold"] = threshold
        else:
            print("error generating graph, heuristic generation not known")
            exit(-1)

        return g

    def model_PO(self, graph: Graph) -> Union[Graph, GraphView]:
        graph_copy = graph
        if self.parameters["Observable"]["Problem"] == "Total":
            return graph_copy
        elif self.parameters["Observable"]["Problem"] == "Partial":
            # Different methods of partial observability
            if "Sample" in self.parameters["Observable"]:
                # "NProbability" = 0.4 means that each node has a 40% chance to be pruned
                if self.parameters["Observable"]["Sample"]["Nodes"] == "Random":
                    graph_copy = GraphView(graph_copy, vfilt=lambda v: ranf() <= self.parameters["Observable"]["Sample"]["NProbability"])
                if self.parameters["Observable"]["Sample"]["Edges"] == "Random":
                    graph_copy = GraphView(graph_copy, efilt=lambda v: ranf() <= self.parameters["Observable"]["Sample"]["EProbability"])
        return graph_copy

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
        json_data = json.dumps({"Data":list(data)})
        # Model used, graph generation
        title = self.parameters["Models"]["Name"] + "_" + self.parameters["Graphs"]["Generation"] + "_" + self.parameters["Heuristics"] + "_"
        if self.parameters["Observable"]["Problem"] == "Total":
            title += "Observable"
        elif self.parameters["Observable"]["Sample"]["Nodes"] == "Random":
            title += "Sample-Nodes-R-" + str(self.parameters["Observable"]["Sample"]["NProbability"])
        elif self.parameters["Observable"]["Sample"]["Edges"] == "Random":
            title += "Sample-Edges-R-" + str(self.parameters["Observable"]["Sample"]["EProbability"])
        with open(title + ".json", "w") as f:
            json.dump(json_data, f)
