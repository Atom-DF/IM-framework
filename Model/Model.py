from graph_tool import Graph
from typing import Callable, List
from abc import ABC, abstractmethod

class Model(ABC):
    def __init__(self, graph: Graph = None, seed_set = None):
        super(Model, self).__init__()
        self._graph = graph
        self._seed_set = seed_set

    @property
    def seed_set(self) -> List[int]:
        return self._seed_set

    @seed_set.setter
    def seed_set(self, value: List[int]):
        self._graph = value

    @property
    def graph(self) -> Graph:
        return self._graph

    @graph.setter
    def graph(self, value: Graph):
        self._graph = value

    def simulate(self):
        if self._graph is None:
            raise Exception("Graph is not defined")
        elif self.seed_set is None:
            raise Exception("Seed set is not defined")
        value = max(self.graph.get_vertices()) + 1
        for v in self.seed_set:
            self.graph.vertex_properties["active"][v] = value

        self._simulate(value)

    @abstractmethod
    def _simulate(self, t):
        raise NotImplementedError


