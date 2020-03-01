from abc import ABC, abstractmethod
from graph_tool import Graph
from typing import List

class Heuristic(ABC):
    @staticmethod
    @abstractmethod
    def generate(g: Graph, size: int) -> List:
        pass



