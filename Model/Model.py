from graph_tool import Graph
from typing import Callable
from abc import ABC, abstractmethod

class Model(ABC):
    def __init__(self, graph: Graph = None, heuristic: Callable = None, seed_set_size: int = None):
        super(Model, self).__init__()
        self._graph = graph
        self._heuristic = heuristic
        self._seed_set_size = seed_set_size
        self._result = None

    @property
    def seed_set_size(self):
        return self._seed_set_size

    @seed_set_size.setter
    def seed_set_size(self, value: int):
        self._seed_set_size = value

    @property
    def heuristic(self):
        return self._heuristic

    @heuristic.setter
    def heuristic(self, value: Callable):
        self._heuristic = value

    @property
    def graph(self) -> Graph:
        return self._graph

    @graph.setter
    def graph(self, value: Graph):
        self._graph = value

    def simulate(self):
        if self._graph is None or self._heuristic is None or self._seed_set_size is None:
            raise Exception("Graph, heursitic or seed_set_size is not defined")
        self.graph = self.heuristic.generate(self.graph, self.seed_set_size)
        self.result = self._simulate()

    @abstractmethod
    def _simulate(self):
        pass

    def _generate_default_graph(self):
        raise NotImplementedError

