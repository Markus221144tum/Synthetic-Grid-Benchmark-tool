import pandapower as pp
import networkx as nx
from pandapower.topology import create_nxgraph

class Network:
    """
    Diese Klasse stellt einen Wrapper um ein pandapower-Netz dar.
    Sie speichert intern einen NetworkX-Graphen für topologische Analysen
    und bietet komfortablen Zugriff auf verschiedene Netzwerkmetriken.
    """

    def __init__(self):
        # NetworkX-Graph, abgeleitet aus pandapower-Netzwerk
        self.graph = None
        # Originales pandapower-Netzwerk für Systemmetriken
        self.pp_net = None

    @classmethod
    def from_pandapower(cls, pp_net: pp.pandapowerNet):
        """Erzeugt eine Network-Instanz aus einem bestehenden pandapower-Netz."""
        inst = cls()
        # Erzeugt NetworkX-Graph, inklusive Leitungen und Transformatoren
        inst.graph = create_nxgraph(pp_net, include_lines=True, include_trafos=True)
        inst.pp_net = pp_net
        return inst

    @classmethod
    def from_json(cls, json_file_path: str):
        """Lädt ein pandapower-Netz aus einer JSON-Datei und erzeugt daraus eine Network-Instanz."""
        pp_net = pp.from_json(json_file_path)
        return cls.from_pandapower(pp_net)

    def get_node_degrees(self) -> list:
        """Gibt eine Liste mit Knotengraden (Anzahl der Verbindungen pro Knoten) zurück."""
        simpleG = nx.Graph(self.graph)
        return [deg for _, deg in simpleG.degree()]

    def get_clustering_dict(self) -> dict:
        """Berechnet den Cluster-Koeffizienten jedes Knotens im Graphen."""
        simpleG = nx.Graph(self.graph)
        return nx.clustering(simpleG)

    def get_shortest_path_lengths(self) -> dict:
        """Berechnet alle kürzesten Pfadlängen zwischen allen Knotenpaaren."""
        simpleG = nx.Graph(self.graph)
        return dict(nx.all_pairs_shortest_path_length(simpleG))

    def get_diameter(self) -> float:
        """Berechnet den Durchmesser (längster kürzester Pfad) des größten zusammenhängenden Teilgraphen."""
        simpleG = nx.Graph(self.graph)
        if not nx.is_connected(simpleG):
            comps = nx.connected_components(simpleG)
            largest = max(comps, key=len)
            subG = simpleG.subgraph(largest)
            return float(nx.diameter(subG))
        else:
            return float(nx.diameter(simpleG))

    def get_betweenness(self) -> dict:
        """Berechnet die Betweenness-Centrality aller Knoten (wie oft liegt ein Knoten auf kürzesten Pfaden)."""
        simpleG = nx.Graph(self.graph)
        return nx.betweenness_centrality(simpleG)

    # Zugriffshilfen für Systemmetriken basierend auf pandapower-Objekten:
    @property
    def lines(self):
        """Gibt alle Leitungen des Netzes zurück."""
        return self.pp_net.line.itertuples()

    @property
    def buses(self):
        """Gibt alle Knoten (Busse) des Netzes zurück."""
        return self.pp_net.bus.itertuples()

    @property
    def transformers(self):
        """Gibt alle Transformatoren des Netzes zurück."""
        return self.pp_net.trafo.itertuples()

    @property
    def loads(self):
        """Gibt alle Lasten des Netzes zurück."""
        return self.pp_net.load.itertuples()

    @property
    def generators(self):
        """Gibt alle Generatoren des Netzes zurück."""
        return self.pp_net.gen.itertuples()

    @property
    def num_customers(self):
        """Berechnet die Gesamtzahl der Kunden im Netz, sofern angegeben."""
        if 'num_customers' in self.pp_net.load.columns:
            return int(self.pp_net.load['num_customers'].sum())
        return None
