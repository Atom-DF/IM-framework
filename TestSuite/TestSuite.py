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

    def __init__(self, params="parameters.json", params_dict=None, graph_name=None):
        try:
            if params_dict is None:
                with open(params, "r") as fp:
                    self.parameters = json.load(fp)
            else:
                self.parameters = params_dict
        except Exception as e:
            print("error parsing the parameters: \n" + str(e))
            exit(-1)

        self.pre_influence(graph_name)

    def pre_influence(self, graph_name=None):
        models = {"IC": IndependantCascade, "LT": LinearThreshold}
        heuristics = {"Random": Random, "Degree": DegreePriority, "SingleDiscount": SingleDiscount, "TIM": TIM}

        try:
            self.model = models[self.parameters["Models"]["Name"]]
        except Exception as e:
            print("Could not find the model in the map: " + self.parameters["Models"]["Name"])
            exit(-1)

        try:
            print("using " + self.parameters["Heuristics"])
            self.heuristic = heuristics[self.parameters["Heuristics"]]
        except Exception as e:
            print("Could not find the heuristic in the map:" + self.parameters["Heuristics"])
            exit(-1)

        # Get the initial graph
        if graph_name is None:
            self.graph = self.gen_graph()
            # Model Partial Obversability
            self.graph_modeled = self.model_PO(self.graph.copy())
        else:
            self.graph = load_graph(graph_name + ".xml.gz")
            self.graph_modeled = load_graph(graph_name + "_modeled.xml.gz")

        self.run_influence()

    def run_influence(self):
        # used for stats
        influence_average = []
        for seedsetsize in self.parameters["SeedSetSize"]:
            results_on_r = []
            if self.parameters["Observable"]["Multiple_Runs"] == 1:
                # Run the heuristic on it
                seed_set = self.heuristic.generate(self.graph_modeled.copy(), seedsetsize)

                # Run R times to make sure it is right !
                results_on_r = self.run_on_R(self.graph, seed_set)
            else:
                heuristic_split = self.heuristic_split(seedsetsize)
                # create two functinos, one for split the other for no split
                results_on_r = self.run_on_split(self.graph.copy(), heuristic_split)

            # Gives the average spread
            average_influence = self.R_stats(results_on_r)

            print(str(seedsetsize) + ": " + str(average_influence))

            influence_average.append(average_influence)
        self.store(influence_average, "Influence_average")

    def heuristic_split(self, seedsetsize):
        multiple_runs = self.parameters["Observable"]["Multiple_Runs"]
        if multiple_runs < 1:
            return [seedsetsize]
        if seedsetsize <= multiple_runs:
            return [1]*seedsetsize
        temp = int(seedsetsize / multiple_runs)
        temp2 = seedsetsize % multiple_runs
        split = [temp]*multiple_runs
        split[-1] += temp2
        return split

    def run_on_split(self, graph, split_seedset):
        # Used for stats
        results_on_r = []
        for i in range(self.parameters["R"]):
            # make two versions of of each heuristic, once where you ignore rest of graph and one where you take into account the effects to generate a "true" seed set

            graph_run = graph.copy()
            edge_filt = self.graph_modeled.get_edge_filter()
            node_filt = self.graph_modeled.get_vertex_filter()

            graph_heuristic = GraphView(graph_run)
            # put the filters back on
            graph_heuristic.set_filters(edge_filt[0], node_filt[0])

            for split in split_seedset:
                # Run the heuristic on it
                seed_set = self.heuristic.generate(graph_heuristic, split)

                # Run the model on the original graph (all changes made by the heuristic are passed onto graph_copy_R)
                result = self.model(graph_run, seed_set)

                # Run the simulation
                result.simulate()
            # Some stats
            results_on_r.append(graph_run)
        return results_on_r

    def run_on_R(self, graph, seed_set):
        # Used for stats
        results_on_r = []
        for i in range(self.parameters["R"]):
            # Run the model on the original graph (all changes made by the heuristic are passed onto graph_copy_R)
            result = self.model(graph.copy(), seed_set)

            # Run the simulation
            result.simulate()
            # Some stats
            results_on_r.append(result.graph)
        return results_on_r

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
        if self.parameters["Save"]:
            self.graph.save("graph.xml.gz")
            graph_copy.save("graph_modeled.xml.gz")
            exit(1)
        if self.parameters["Observable"]["Problem"] == "Total":
            return graph_copy
        elif self.parameters["Observable"]["Problem"] == "Partial":
            # Different methods of partial observability
            if "Sample" in self.parameters["Observable"]:
                # "NProbability" = 0.4 means that each node has a 40% chance to be pruned
                if self.parameters["Observable"]["Sample"]["Nodes"] == "Random":
                    graph_copy = GraphView(graph_copy, vfilt=lambda v: ranf() <= self.parameters["Observable"]["Sample"]["NProbability"])
                # elif self.parameters["Observable"]["Sample"]["Nodes"] == "MaxDeg":
                #     graph_copy = GraphView()
                if self.parameters["Observable"]["Sample"]["Edges"] == "Random":
                    graph_copy = GraphView(graph_copy, efilt=lambda v: ranf() <= self.parameters["Observable"]["Sample"]["EProbability"])
        return graph_copy

    def R_stats(self, gs: List[Graph]) -> int:
        # average number of the influence
        xs = zeros(1)
        for g in gs:
            x = vertex_hist(g, g.vertex_properties["active"], [0, 1])
            xs = [x+y for x, y in zip_longest(xs, x[0], fillvalue=0)]
        # The average for this graph on R
        xs = divide(xs, len(gs))
        # Return the number of influenced nodes
        return sum(xs[1:])

    def store(self, data, name):
        json_data = json.dumps({"Data": list(data)})
        # Model used, graph generation
        title = self.parameters["Models"]["Name"]+ str(self.parameters["Models"]["Degree_Based"]) + "_" + \
                self.parameters["Graphs"]["Generation"] + "_NRun" + str(self.parameters["Observable"]["Multiple_Runs"]) + \
                "_" + self.parameters["Heuristics"] + "_"
        if self.parameters["Observable"]["Problem"] == "Total":
            title += "Observable"
        elif self.parameters["Observable"]["Sample"]["Nodes"] == "Random":
            title += "Sample-Nodes-R-" + str(self.parameters["Observable"]["Sample"]["NProbability"])
        elif self.parameters["Observable"]["Sample"]["Edges"] == "Random":
            title += "Sample-Edges-R-" + str(self.parameters["Observable"]["Sample"]["EProbability"])
        with open(title + ".json", "w") as f:
            json.dump(json_data, f)
