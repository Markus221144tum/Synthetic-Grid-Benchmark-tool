import os
import pandapower as pp
from multiprocessing import Pool, cpu_count
from real_vs_synth.model.network import Network

def process_json_file(args):
    file, root = args
    full_path = os.path.join(root, file)
    pp_net = pp.from_json(full_path)
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
    return (level, net_obj, file, mean_vn, vn_values)

class SyntheticLoader:
    """
    Lädt ein Verzeichnis von Pandapower-JSON-Netzen parallel.
    Jede JSON-Datei wird eingelesen, als pandapower-Netz erzeugt
    und anschließend in Network konvertiert. Konsolenausgabe wie gewohnt.
    """
    def __init__(self, base_folder: str):
        self.base_folder = base_folder

    def load(self, path: str = None) -> dict:
        result = {"EHV": [], "HV": [], "MV": [], "LV": []}
        file_args = []
        for root, _, files in os.walk(self.base_folder):
            for file in files:
                if file.lower().endswith(".json"):
                    file_args.append((file, root))

        with Pool(min(cpu_count(), 8)) as pool:
            loaded = pool.map(process_json_file, file_args)
        for level, net_obj, file, mean_vn, vn_values in loaded:
            result[level].append(net_obj)
            print(f"Lade {file}: Datei einlesen…")
            print(f"  gefundene vn_kv-Werte = {vn_values}")
            print(f"  ⇒ mittlerer vn_kv = {mean_vn:.3f}")
            print(f"  ⇒ {file} wird als {level} erkannt (mean vn_kv = {mean_vn:.3f})")
        return result
