import json
from graph_tool.all import *
from numpy.random import ranf, randint
from Model.Model import Model
from Model.IndependantCascade import IndependantCascade
from Heuristic.Heuristic import Heuristic
from Heuristic.Random import Random
from Heuristic.DegreePriority import DegreePriority

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

        results = list()
        for seedsetsize in parameters["SeedSetSize"]:
            average = list()
            Results_R = list()
            for NumGraphs in range(parameters["NumGraphs"]):
                graph = self.gen_graph(parameters["Graphs"]["Cardinality"], parameters["Graphs"]["Density"], parameters["Models"]["IC"]["Propagation"])
                temp_average = 0
                Results_R_temp = list()
                for i in range(parameters["R"]):
                    result = IndependantCascade(graph.copy(), Random, seedsetsize)
                    result.simulate()
                    g = GraphView(result.graph, vfilt=lambda v: result.graph.vertex_properties["active"][v] > 0)
                    Results_R_temp.append(len(g.get_vertices()))
                    temp_average += len(g.get_vertices())
                # print(Results_R_temp)
                average.append([str(NumGraphs), int(temp_average/parameters["R"])])
                Results_R.append([str(NumGraphs), Results_R_temp])
                # print(Results_R)
            results.append([str(seedsetsize), average, Results_R])
        # print(results)
        data = json.dumps(results)
        with open("results.json", "w") as fp:
            json.dump(data, fp)

    def gen_graph(self, size, density, propagation):
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