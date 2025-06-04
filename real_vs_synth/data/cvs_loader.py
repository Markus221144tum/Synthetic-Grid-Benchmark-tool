import os
import pandapower as pp
from real_vs_synth.model.network import Network

class CsvLoader:
    """
    Lädt Verzeichnisse, die CSV-Dateien enthalten, aus denen sich
    Pandapower-Netze rekonstruieren lassen.
    """

    def __init__(self, base_folder: str):
        self.base_folder = base_folder

    def load(self, path: str = None) -> dict:
        """
        Scannt self.base_folder nach Unterordnern, die CSV-Dateien enthalten:
        Erwartet Struktur:
          <base_folder>/<Netzname>/bus.csv, line.csv, trafo.csv, etc.
        Liest mit 'pp.from_csv_folder()' das Pandapower-Netz ein,
        bestimmt Spannungsebene, wandelt in Network um.
        """
        result = {"EHV": [], "HV": [], "MV": [], "LV": []}

        # Suche nach Unterordnern mit bus.csv
        for sd in os.listdir(self.base_folder):
            folder_path = os.path.join(self.base_folder, sd)
            if not os.path.isdir(folder_path):
                continue
            bus_file = os.path.join(folder_path, "bus.csv")
            if not os.path.isfile(bus_file):
                continue

            print(f"Lade CSV-Netz aus Ordner: {folder_path}")
            pp_net = pp.from_csv_folder(folder_path)

            # Ebene bestimmen
            vn_values = pp_net.bus["vn_kv"].tolist()
            max_vn = max(vn_values)
            if max_vn > 50:
                level = "EHV"
            elif max_vn > 20:
                level = "HV"
            elif max_vn > 1:
                level = "MV"
            else:
                level = "LV"
            print(f"  ⇒ erkannt als {level} (max vn_kv = {max_vn})")

            net_obj = Network.from_pandapower(pp_net)
            result[level].append(net_obj)

        return result