import numpy as np
import networkx as nx


def compute_node_degree_metrics(network):
    """
    Berechnet die Knotengradmetriken (mean, std, Verteilung) eines Netzwerks.

    Knotengrad k_i eines Knotens i ist die Anzahl direkt benachbarter Knoten.
    Es wird ein einfacher (ungerichteter) Graph verwendet, um doppelte Kanten
    (z. B. durch parallele Leitungen) zusammenzufassen.

    Rückgabe:
    - Mittelwert des Knotengrads
    - Standardabweichung
    - Liste aller Knotengrade (zur Histogramm-/Boxplot-Auswertung)
    """
    G = nx.Graph(network.graph)
    degrees = np.array([deg for _, deg in G.degree()])
    return float(np.mean(degrees)), float(np.std(degrees)), degrees.tolist()


def compute_clustering_coefficient(network):
    """
    Berechnet den lokalen Clustering-Koeffizienten für jeden Knoten und gibt
    Mittelwert, Standardabweichung sowie alle Einzelwerte zurück.
    """
    mg = network.graph
    unique_edges = set((min(u, v), max(u, v)) for u, v in mg.edges())
    G_simple = nx.Graph()
    G_simple.add_edges_from(unique_edges)
    clustering_dict = nx.clustering(G_simple)
    values = np.array(list(clustering_dict.values()))
    return float(np.mean(values)), float(np.std(values)), values.tolist()


def compute_characteristic_path_length(network):
    """
    Berechnet durchschnittliche Pfadlänge (mean) auf der größten Komponente.

    Zusätzlich wird die Liste aller Pfadlängen (d_ij) zurückgegeben.
    """
    G = nx.Graph(network.graph)
    if not nx.is_connected(G):
        largest = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest)
    path_len_dict = dict(nx.all_pairs_shortest_path_length(G))
    path_lengths = [d for lengths in path_len_dict.values() for d in lengths.values() if d > 0]
    avg = float(np.mean(path_lengths)) if path_lengths else 0.0
    return avg, 0.0, path_lengths  # stddev bleibt 0.0


def compute_graph_diameter(network):
    """
    Berechnet den Durchmesser der größten zusammenhängenden Komponente.
    
    Kein Streuungswert sinnvoll, daher nur einzelner Wert + leere Liste.
    """
    G = nx.Graph(network.graph)
    if not nx.is_connected(G):
        largest = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest)
    return float(nx.diameter(G)), []


def compute_betweenness_centrality(network):
    """
    Berechnet die Betweenness Centrality aller Knoten
    und gibt Mittelwert, Standardabweichung sowie Einzelwerte zurück.
    """
    G = nx.Graph(network.graph)
    bc_dict = nx.betweenness_centrality(G)
    values = np.array(list(bc_dict.values()))
    return float(np.mean(values)), float(np.std(values)), values.tolist()
