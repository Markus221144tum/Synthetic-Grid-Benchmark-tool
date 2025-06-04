import numpy as np
import networkx as nx

def compute_node_degree_metrics(network):
    """
    Berechnet Mittelwert und StdDev des Knotengrads. 
    Verwendet einfachen Graph, um Multi-Kanten zusammenzufassen.
    """
    G = nx.Graph(network.graph)
    degrees = np.array([deg for _, deg in G.degree()])
    return float(np.mean(degrees)), float(np.std(degrees))

def compute_clustering_coefficient(network):
    """
    Berechnet lokalen Clustering Coeff ci für jeden Knoten:
    ci = 2·ei / (ki·(ki−1)), wobei ei = Anzahl Dreiecke um i, ki = Knotengrad.
    Liefert Mittelwert und StdDev.
    """
    mg = network.graph
    unique_edges = set()
    for u, v in mg.edges():
        if u <= v:
            unique_edges.add((u, v))
        else:
            unique_edges.add((v, u))
    G_simple = nx.Graph()
    G_simple.add_edges_from(unique_edges)
    clustering_dict = nx.clustering(G_simple)
    values = np.array(list(clustering_dict.values()))
    return float(np.mean(values)), float(np.std(values))

def compute_characteristic_path_length(network):
    """
    Berechnet ⟨l⟩ = (1/(|V|·(|V|−1))) · Σ_{i≠j} d_{ij},
    wobei d_{ij} die kürzeste Pfadlänge zwischen i und j ist.
    Falls Graph nicht zusammenhängend, wird größte Komponente verwendet.
    Liefert Mittelwert (StdDev wird 0 gesetzt).
    """
    G = nx.Graph(network.graph)
    if not nx.is_connected(G):
        comps = nx.connected_components(G)
        largest = max(comps, key=len)
        G = G.subgraph(largest)
    n = G.number_of_nodes()
    if n < 2:
        return 0.0, 0.0
    path_len_dict = dict(nx.all_pairs_shortest_path_length(G))
    total = 0.0
    count = 0
    for i, lengths in path_len_dict.items():
        for j, d in lengths.items():
            if i != j:
                total += d
                count += 1
    avg = total / count if count > 0 else 0.0
    return float(avg), 0.0

def compute_graph_diameter(network):
    """
    Berechnet den Graph-Durchmesser D_max = max_{i≠j} d_{ij} für größte zusammenhängende Komponente.
    """
    G = nx.Graph(network.graph)
    if not nx.is_connected(G):
        comps = nx.connected_components(G)
        largest = max(comps, key=len)
        G = G.subgraph(largest)
    return float(nx.diameter(G))

def compute_betweenness_centrality(network):
    """
    Berechnet Betweenness Centrality b_i = Σ_{s≠i≠t} σ_st(i) / σ_st für jeden Knoten.
    Liefert Mittelwert und StdDev.
    """
    G = nx.Graph(network.graph)
    bc_dict = nx.betweenness_centrality(G)
    values = np.array(list(bc_dict.values()))
    return float(np.mean(values)), float(np.std(values))