from abc import ABC, abstractmethod
from graph_tool import Graph

class Heuristic(ABC):
    @staticmethod
    @abstractmethod
    def generate(g: Graph, size: int) -> Graph:
        pass



