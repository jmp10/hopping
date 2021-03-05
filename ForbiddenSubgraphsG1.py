import networkx as nx
from itertools import combinations


# Shortens a list of graphs to remove any isomorphisms.
def remove_isomorphisms(graph_list):
    to_delete_list = []
    for i in range(len(graph_list)):
        if i % 50 == 0:  # progress bar
            print("Finished " + str(i) + " of " + str(len(graph_list)) + "...")

        for j in range(i + 1, len(graph_list)):
            if nx.faster_could_be_isomorphic(graph_list[i], graph_list[j]):
                if nx.fast_could_be_isomorphic(graph_list[i], graph_list[j]):
                    if nx.is_isomorphic(graph_list[i], graph_list[j]):
                        to_delete_list += [i]
                        break

    for index in sorted(to_delete_list, reverse=True):
        del graph_list[index]
    return graph_list


# Removes graphs from a list that are induced supergraphs of another graph in the list.
def remove_supergraphs(graph_list):
    supergraph_index_list = []

    for i in range(len(graph_list)):
        if i % 50 == 0:  # progress bar
            print("Finished " + str(i) + " of " + str(len(graph_list)) + "...")

        possible_supergraph = graph_list[i].copy()

        for j in range(len(graph_list)):
            possible_subgraph = graph_list[j].copy()

            # If the two graphs aren't the same and possible_supergraph has more vertices than possible_subgraph...
            if i != j and possible_supergraph.order() > possible_subgraph.order():
                # ...check to see if possible_subgraph is an induced subgraph of possible_supergraph using the
                # ISMAGS algorithm.
                ismags = nx.isomorphism.ISMAGS(possible_supergraph, possible_subgraph)
                if nx.algorithms.isomorphism.ISMAGS.subgraph_is_isomorphic(ismags):
                    supergraph_index_list += [i]
                    break

    for index in sorted(supergraph_index_list, reverse=True):
        del graph_list[index]
    return graph_list


# G_1 consists of graphs in M_2 and M_{1,1}. So, to begin, we generate a set of all possible 2- and (1,1)-hopping
# accelerators from their "parent" graphs by deleting every possible subset of edges.
M2_parent = nx.Graph()
M2_edges = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]
M2_parent.add_edges_from(M2_edges)  # 2K_3
M2_edge_subsets = [list(subset) for i in range(len(M2_edges) + 1) for subset in combinations(M2_edges, i)]

# Generate all possible 2-hopping accelerators:
M2_graphs = []
for edges_to_delete in M2_edge_subsets:  # For each subset, delete them from the parent graph to get a new 2-h.a.
    new_graph = M2_parent.copy()
    new_graph.remove_edges_from(edges_to_delete)
    M2_graphs += [new_graph]

# There are three parent graphs in M_{1,1}, depending on how many vertices (0, 1, or 2) are in the intersection of T_1
# and S_2. As such, we will do the above process for each of these three parent graphs.

# M_{1,1} parent graph a with 2 vertices in T_1 intersect S_2
M11a = nx.Graph()
M11a.add_edges_from([(0, 1), (2, 3), (4, 5)])

# M_{1,1} parent graph b with 1 vertex in T_1 intersect S_2
M11b = nx.Graph()
M11b.add_edges_from([(1, 2), (1, 5), (2, 5), (3, 4), (4, 5), (3, 5), (3, 6), (3, 7), (6, 7)])

# M_{1,1} parent graph c with 0 vertices in T_1 intersect S_2
M11c = nx.Graph()
M11c.add_edges_from([(1, 2), (1, 5), (1, 6), (2, 5), (2, 6),
                     (3, 4), (4, 5), (5, 6), (3, 5), (4, 6), (3, 6),
                     (3, 7), (3, 8), (4, 7), (4, 8), (7, 8)])

M11_parents = [M11a, M11b, M11c]

# Generate all possible (1,1)-hopping accelerators:
M11_graphs = []
for M11x in M11_parents:
    M11x_edges = list(M11x.edges())
    M11x_edge_subsets = [list(subset) for i in range(len(M11x_edges) + 1) for subset in combinations(M11x_edges, i)]
    M11x_graphs = []
    for edges_to_delete in M11x_edge_subsets:  # For each subset, delete them from the parent graph to get a new h.a.
        new_graph = M11x.copy()
        new_graph.remove_edges_from(edges_to_delete)
        M11_graphs += [new_graph]

# Combine M2_graphs and M11_graphs together, and remove all the duplicate isomorphic graphs within.
G1_graphs = M2_graphs + M11_graphs
remove_isomorphisms(G1_graphs)

# Remove all graphs in G1_graphs that are a supergraph of another graph in the list.
remove_supergraphs(G1_graphs)
print("The number of graphs in G_1 is: " + str(len(G1_graphs)))

# Convert the graphs in G1_graphs to graph6 format, so they can be more easily visualized using Mathematica.
# The list comprehension below decodes the graph6 bytes to strings.
G1_graphs_g6 = [nx.to_graph6_bytes(graph, header=False).decode("utf-8") for graph in G1_graphs]

# Write the list of graphs (in graph6 format) to a text file.
with open("g1graphs.txt", "w") as file:
    for graph in G1_graphs_g6:
        file.write(graph)
