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
from Graphs.Random import RandomGraph
from Graphs.ScaleFree import ScaleFreeGraph
from numpy.random import normal
from numpy import divide, zeros
from typing import List, Union
import plotly.graph_objects as go
from itertools import zip_longest
from time import time


class TestSuite:

    def __init__(self, params="parameters.json", params_dict=None):
        try:
            if params_dict is None:
                with open(params, "r") as fp:
                    self.parameters = json.load(fp)
            else:
                self.parameters = params_dict
        except Exception as e:
            print("error parsing the parameters: \n" + str(e))
            exit(-1)

        # create a map with models, one with heuristics
        # whenever there is an array create a job with each of the values (only support one array at a time to start with)
        # Go through each job. and store the results

        models = {"IC": IndependantCascade, "LT": LinearThreshold}
        heuristics = {"Random": Random, "Degree": DegreePriority, "SingleDiscount": SingleDiscount, "TIM": TIM}

        try:
            self.model = models[self.parameters["Models"]["Name"]]
        except Exception as e:
            print("Could not find the model in the map: " + self.parameters["Models"]["Name"])
            exit(-1)

        try:
            print("using "+self.parameters["Heuristics"])
            self.heuristic = heuristics[self.parameters["Heuristics"]]
        except Exception as e:
            print("Could not find the heuristic in the map:" + self.parameters["Heuristics"])
            exit(-1)

        # Get the initial graph
        self.graph = self.gen_graph()

        # Model Partial Obversability
        graph = self.model_PO(self.graph.copy())

        # used for stats
        influence_average = []
        for seedsetsize in self.parameters["SeedSetSize"]:
            # Used for stats
            results_on_r = []

            # Copy of the graph for the run
            graph_copy = graph.copy()

            # Run the heuristic on it
            seed_set = self.heuristic.generate(graph_copy, seedsetsize)
            for i in range(self.parameters["R"]):
                # Use a blank graph, the changes from the heuristic are kept in this version
                graph_copy_R = graph_copy.copy()
                # Run the model on the original graph (all changes made by the heuristic are passed onto graph_copy_R)
                result = self.model(graph_copy_R, seed_set)

                # Run the simulation
                result.simulate()
                # Some stats
                results_on_r.append(result.graph)
            # Gives the average spread
            average_influence = self.R_stats(results_on_r)
            print(str(seedsetsize) + ": " + str(average_influence))
            influence_average.append(average_influence)
        self.store(influence_average, "Influence_average")

    def gen_graph(self):
        if self.parameters["Graphs"]["Generation"] == "R":
            generator = RandomGraph(self.parameters["Graphs"]["Cardinality"])
            g = generator.generate()
        elif self.parameters["Graphs"]["Generation"] == "SF":
            generator = ScaleFreeGraph(self.parameters["Graphs"]["Cardinality"], self.parameters["Graphs"]["Gamma"], self.parameters["Graphs"]["Out-degree"])
            g = generator.generate()
        self.model.set_up(g, self.parameters["Models"])
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
