import os
import pandapower as pp
from multiprocessing import Pool, cpu_count
from real_vs_synth.model.network import Network

def process_csv_folder(folder_path):
    try:
        pp_net = pp.from_csv_folder(folder_path)
    except Exception as e:
        return (None, None, folder_path, None, None, str(e))
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
    return (level, net_obj, folder_path, mean_vn, vn_values, None)

class CsvLoader:
    """
    Lädt ein Verzeichnis mit Unterordnern, die jeweils CSV-Dateien
    für ein Pandapower-Netz enthalten (bus.csv, line.csv, etc.), parallel.
    Funktioniert rekursiv und erkennt automatisch die Spannungsebene.
    """
    def __init__(self, base_folder: str):
        self.base_folder = base_folder

    def load(self, path: str = None) -> dict:
        result = {"EHV": [], "HV": [], "MV": [], "LV": []}
        folder_args = []
        for root, dirs, files in os.walk(self.base_folder):
            if "bus.csv" in files:
                folder_args.append(root)

        with Pool(min(cpu_count(), 8)) as pool:
            loaded = pool.map(process_csv_folder, folder_args)
        for level, net_obj, folder_path, mean_vn, vn_values, error in loaded:
            print(f"Lade CSV-Netz aus Ordner: {folder_path}")
            if error is not None:
                print(f"  Fehler beim Laden von {folder_path}: {error}")
                continue
            print(f"  gefundene vn_kv-Werte = {vn_values}")
            print(f"  ⇒ mittlerer vn_kv = {mean_vn:.3f}")
            print(f"  ⇒ erkannt als {level} (mean vn_kv = {mean_vn:.3f})")
            result[level].append(net_obj)
        return result
