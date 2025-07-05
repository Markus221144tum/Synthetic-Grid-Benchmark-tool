import os
import pickle
from multiprocessing import Pool, cpu_count
from real_vs_synth.model.network import Network

def process_pkl_file(args):
    file, root = args
    full_path = os.path.join(root, file)
    with open(full_path, "rb") as f:
        dingo_net = pickle.load(f)
    nets = dingo_net if isinstance(dingo_net, list) else [dingo_net]
    results = []
    for net_idx, d_net in enumerate(nets):
        if hasattr(d_net, "bus") and hasattr(d_net, "line"):
            pp_net = d_net
        elif isinstance(d_net, dict) and "pp_net" in d_net:
            pp_net = d_net["pp_net"]
        elif hasattr(d_net, "to_pandapower"):
            pp_net = d_net.to_pandapower()
        else:
            continue
        vn_values = pp_net.bus["vn_kv"].tolist()
        mean_vn = sum(vn_values) / len(vn_values) if vn_values else 0.0
        if mean_vn > 50:
            level = "EHV"
        elif mean_vn > 20:
            level = "HV"
        elif mean_vn > 5:
            level = "MV"
        else:
            level = "LV"
        net_obj = Network.from_pandapower(pp_net)
        # Ergebnis als Tupel mit allen Infos zurückgeben!
        results.append((level, net_obj, file, net_idx+1, mean_vn))
    return results

class DingoLoader:
    """
    Paralleles Laden von Dingo-PKL-Netzen. Gibt Datei, Spannungsebene und Mittelwert vn_kv aus.
    """
    def __init__(self, base_folder: str):
        self.base_folder = base_folder

    def load(self, path: str = None) -> dict:
        result = {"EHV": [], "HV": [], "MV": [], "LV": []}
        file_args = []
        for root, _, files in os.walk(self.base_folder):
            for file in files:
                if file.lower().endswith(".pkl"):
                    file_args.append((file, root))

        with Pool(min(cpu_count(), 8)) as pool:
            results_nested = pool.map(process_pkl_file, file_args)
        for res in results_nested:
            for level, net_obj, file, net_idx, mean_vn in res:
                result[level].append(net_obj)
                # Ausgabe im Hauptprozess!
                print(f"  ⇒ {file} [Netz {net_idx}] wird als {level} erkannt (mean vn_kv = {mean_vn:.3f})")
        return result