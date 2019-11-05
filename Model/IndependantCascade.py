from graph_tool.all import *
from numpy.random import ranf, randint, choice

# TEMP
size = 500

class IndependantCascade:
    pass

def IC(g: Graph, t: int) -> Graph:
    # Go through recently activated nodes
    g_ = GraphView(g, vfilt= lambda v: active[v] == t)
    for n in g_.vertices():
        # Go through the neighboors
        v = g.vertex(n)
        for e_neighbour, n_neighbour in zip(v.out_edges(), v.out_neighbors()):
            # Check if the node is activated and make sure not to give it a second life
            if weight[e_neighbour] > ranf(1) and active[n_neighbour] == 0:
                active[n_neighbour] = t+1
    # TODO fix this bug wtf
    if t == size:
        return g
    return IC(g, t + 1)

# Take in a directed weighted graph where the weights are between 0 and 1 included (?)
# Go through all previously activated nodes and try to activate their neighbours
# loop

# Create the graph
g = Graph()

# Add the vertexes
g.add_vertex(size)

# insert some random links
for s,t in zip(randint(0, size, size*4), randint(0, size, size*4)):
    e = g.add_edge(g.vertex(s), g.vertex(t))

# Problem specific edits to the graph
weight = g.new_edge_property("double", vals=ranf(size))

# Seed set
active = g.new_vertex_property("int")
for s in choice(range(size), 10):
    active[g.vertex(s)] = 1

total = 0

for v in g.vertices():
    if active[v] > 0:
        total+=1

print(total)

g = IC(g, 1)

total = 0
for v in g.vertices():
    if active[v] > 0:
        total+=1

print(total)

graph_draw(g, output_size=(10000, 10000), output="graph.png")