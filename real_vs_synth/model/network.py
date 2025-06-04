import pandapower as pp
import networkx as nx
from pandapower.topology import create_nxgraph

class Network:
    """
    Wrapper um ein Pandapower-Netz, das den internen Graph (NetworkX) speichert und
    Zugriff auf Topologie-Metriken bietet.
    """
    def __init__(self):
        self.graph = None  # NetworkX-Graph
        self.pp_net = None  # Originales pandapower-Netz für Systemmetriken

    @classmethod
    def from_pandapower(cls, pp_net: pp.pandapowerNet):
        inst = cls()
        inst.graph = create_nxgraph(pp_net, include_lines=True, include_trafos=True)
        inst.pp_net = pp_net
        return inst

    @classmethod
    def from_json(cls, json_file_path: str):
        pp_net = pp.from_json(json_file_path)
        return cls.from_pandapower(pp_net)

    def get_node_degrees(self) -> list:
        simpleG = nx.Graph(self.graph)
        return [deg for _, deg in simpleG.degree()]

    def get_clustering_dict(self) -> dict:
        simpleG = nx.Graph(self.graph)
        return nx.clustering(simpleG)

    def get_shortest_path_lengths(self) -> dict:
        simpleG = nx.Graph(self.graph)
        return dict(nx.all_pairs_shortest_path_length(simpleG))

    def get_diameter(self) -> float:
        simpleG = nx.Graph(self.graph)
        if not nx.is_connected(simpleG):
            comps = nx.connected_components(simpleG)
            largest = max(comps, key=len)
            subG = simpleG.subgraph(largest)
            return float(nx.diameter(subG))
        else:
            return float(nx.diameter(simpleG))

    def get_betweenness(self) -> dict:
        simpleG = nx.Graph(self.graph)
        return nx.betweenness_centrality(simpleG)

    # Zugriffshilfen für Systemmetriken:
    @property
    def lines(self):
        return self.pp_net.line.itertuples()

    @property
    def buses(self):
        return self.pp_net.bus.itertuples()

    @property
    def transformers(self):
        return self.pp_net.trafo.itertuples()

    @property
    def loads(self):
        return self.pp_net.load.itertuples()

    @property
    def generators(self):
        return self.pp_net.gen.itertuples()

    @property
    def num_customers(self):
        if 'num_customers' in self.pp_net.load.columns:
            return int(self.pp_net.load['num_customers'].sum())
        return None