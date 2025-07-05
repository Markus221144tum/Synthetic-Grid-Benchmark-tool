import torch
import os
from real_vs_synth.model.network import Network
import pandapower as pp

# Sicherheitsfreigabe für torch_geometric Data-Objekte
from torch_geometric.data import Data
import torch_geometric.data.data as geom_data

DataEdgeAttr = getattr(geom_data, "DataEdgeAttr", None)
if DataEdgeAttr is not None:
    torch.serialization.add_safe_globals([DataEdgeAttr])
torch.serialization.add_safe_globals([Data])

def load_pt_file(path):
    data = torch.load(path, map_location=torch.device("cpu"), weights_only=False)

    # === Variante 1: Wenn data ein dict ist mit passenden Keys ===
    if isinstance(data, dict) and "edge_index" in data and "num_nodes" in data:
        edge_index = data["edge_index"]
        num_nodes = data["num_nodes"]

    # === Variante 2: Wenn data ein Data-Objekt oder Liste davon ===
    elif isinstance(data, list) and len(data) > 0 and hasattr(data[0], "edge_index") and hasattr(data[0], "num_nodes"):
        data = data[0]
        edge_index = data.edge_index
        num_nodes = data.num_nodes

    elif hasattr(data, "edge_index") and hasattr(data, "num_nodes"):
        edge_index = data.edge_index
        num_nodes = data.num_nodes

    else:
        print(f"DEBUG: Dateiinhalt von {path}:")
        print(f"Typ: {type(data)}")
        print(f"Attribute: {dir(data)}")
        raise ValueError(f"Unerwartetes Datenformat in Datei: {path}")

    net = pp.create_empty_network()

    for _ in range(num_nodes):
        pp.create_bus(net, vn_kv=20.0)

    if "my_line" not in net.std_types["line"]:
        pp.create_std_type(net, {
            "c_nf_per_km": 210,
            "r_ohm_per_km": 0.876,
            "x_ohm_per_km": 0.115,
            "max_i_ka": 0.142,
            "type": "cs",
            "q_mm2": 240,
            "g_us_per_km": 0
        }, name="my_line", element="line")

    edge_index_np = edge_index.numpy()
    for i in range(edge_index_np.shape[1]):
        from_bus = int(edge_index_np[0, i])
        to_bus = int(edge_index_np[1, i])
        if from_bus != to_bus:
            pp.create_line(net, from_bus, to_bus, length_km=1.0, std_type="my_line")

    network = Network.from_pandapower(net)
    network.name = os.path.basename(path).replace(".pt", "")
    return network

def load_pt_folder(folder):
    nets = []
    for file in os.listdir(folder):
        if file.endswith(".pt"):
            full_path = os.path.join(folder, file)
            nets.append(load_pt_file(full_path))
    return nets

class PtLoader:
    def __init__(self, folder: str):
        self.folder = folder

    def load(self, _):
        return {"LV": load_pt_folder(self.folder)}
