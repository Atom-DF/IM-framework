from graph_tool.all import *
from .Heuristic import Heuristic
from timeit import default_timer as timer
from numpy.random import ranf, randint
from numpy import log, exp, log2, sum, vectorize, asarray
from scipy.special import binom
import functools


def timer2(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = timer()  # 1
        value = func(*args, **kwargs)
        end_time = timer()  # 2
        run_time = end_time - start_time  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


class TIM(Heuristic):

    @staticmethod
    # @timer2
    def generate(g: Graph, size: int):
        epsilon = 1
        l = 1
        n = g.num_vertices()
        lambda_ = (8 + 2 * epsilon)*n * (l*log(n) + log(binom(n, size)) + log(2))*(epsilon**(-2))

        KTP = TIM.parameter_estimation(g, size, l)
        theta = lambda_ / KTP
        # shouldn't need to generate that many tbf
        if theta == float('inf'):
            theta = 5000000
        seed_set = TIM.node_selection(g, size, int(theta))
        return seed_set

    @staticmethod
    # @timer2
    def parameter_estimation(G, k, l):
        # @timer2
        def K(R):
            m = G.num_edges()
            # Go over every set and calculate K(set)
            temp = 0
            for i in list(R):
                temp += 1 - (1 - sum(G.get_out_degrees(list(i)))/m)**k
            # return the sum of those
            return temp

        n = G.num_vertices()
        for i in range(1, int(log2(n - 1))):
            c = (6 * l * log(n) + 6 * log(log2(n))) * 2**i
            # Generate c RR sets
            sum_ = K(TIM.rr_generation(G, int(c)))
            if sum_/c > 1/(2**i):
                return n*sum_/(2*c)
        return 1

    @staticmethod
    # @timer2
    def node_selection(G, k, theta):
        # generate theta random RR sets and insert them in R
        R = TIM.rr_generation(G, theta)
        S = set()
        for i in range(k):
            v = TIM.max_cover(R)
            S.add(v)
            R = {j for j in R if v not in j}
        return S

    @staticmethod
    # @timer2
    def rr_generation(G: Graph, theta):
        R = set()
        # print(theta)
        for i in range(theta):
            queue = []
            visited = set()
            v = randint(G.num_vertices())
            temp = G.vertex(v, use_index=False)
            visited.add(temp)
            queue.append(temp)
            while len(queue) != 0:
                curr = queue.pop(0)
                # This TIM verion only works for un directed graphs
                for edge, node in zip(curr.out_edges(), curr.out_neighbors()):
                    if node not in visited and G.edge_properties["weight"][edge] > ranf(1):
                        visited.add(node)
                        queue.append(node)
            R.add(tuple(visited))
        return R

    @staticmethod
    def max_cover(R):
        counter = dict()
        for i in R:
            for j in i:
                counter[j] = counter.get(j, 0) + 1
        return max(counter.items(), key=(lambda key: key[1]))[0]
