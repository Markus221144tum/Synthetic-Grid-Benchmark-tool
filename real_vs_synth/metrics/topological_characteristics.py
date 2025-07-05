import numpy as np
import networkx as nx

def compute_node_degree_metrics(network):
    """
    Berechnet die Knotengradmetriken (mean, std, Verteilung) eines Netzwerks.
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
    G = nx.Graph(network.graph)
    if not nx.is_connected(G):
        largest = max(nx.connected_components(G), key=len)
        G = G.subgraph(largest)
    try:
        d = float(nx.diameter(G))
        return d, [d]  # <== füge den Wert als "Verteilung" hinzu
    except Exception:
        return 0.0, []

def compute_betweenness_centrality(network):
    """
    Berechnet die Betweenness Centrality aller Knoten
    und gibt Mittelwert, Standardabweichung sowie Einzelwerte zurück.
    """
    G = nx.Graph(network.graph)
    bc_dict = nx.betweenness_centrality(G)
    values = np.array(list(bc_dict.values()))
    return float(np.mean(values)), float(np.std(values)), values.tolist()

def compute_degree_assortativity(network):
    """
    Degree Assortativity (ρ): Misst, ob Knoten mit ähnlichem Grad bevorzugt verbunden sind.
    Werte:
        ρ > 0  → hochgradige Knoten verbinden sich eher mit anderen hochgradigen (z. B. soziale Netzwerke).
        ρ < 0  → hochgradige Knoten verbinden sich mit niedriggradigen (z. B. Stromnetze, viele "Sterne").
        ρ ≈ 0  → keine erkennbare Präferenz.
    In realen Stromübertragungsnetzen oft ρ ≈ -0.1 (leicht disassortativ).
    In städtischen MV-Netzen kann ρ ≈ 0.5 (moderat positiv) auftreten.
    Quelle: siehe Literaturhinweis im Chat.
    """
    G = nx.Graph(network.graph)
    if G.number_of_edges() == 0:
        return 0.0  # Nicht definiert, Standardwert 0
    return nx.degree_assortativity_coefficient(G)

def compute_meshness(network):
    """
    Berechnet den Vermaschtheitsgrad (Meshness) des Netzwerks:
        μ = E - N + P
        E: Anzahl Kanten, N: Anzahl Knoten, P: Anzahl Komponenten
    μ = 0: Baum (keine Schleife)
    μ > 0: vermascht
    Quelle: Albert et al., Science 2004.
    """
    G = nx.Graph(network.graph)
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    n_components = nx.number_connected_components(G)
    meshness = n_edges - n_nodes + n_components
    return meshness

# Die Funktion für Meshness (Vermaschtheit) kannst du ebenfalls ergänzen (siehe voriger Post).
