import os
import pandapower as pp
from real_vs_synth.model.network import Network


class SyntheticLoader:
    """
    Lädt ein Verzeichnis von Pandapower-JSON-Netzen.
    Jede JSON-Datei wird eingelesen, als pandapower-Netz erzeugt
    und anschließend in Network konvertiert.
    """

    def __init__(self, base_folder: str):
        self.base_folder = base_folder

    def load(self, path: str = None) -> dict:
        """
        Scannt rekursiv self.base_folder nach .json-Dateien.
        Bestimmt anhand des mittleren vn_kv-Werts den Spannungsebene (LV/MV/HV/EHV)
        und sortiert entsprechend in das Rückgabe-Dict ein.
        """
        result = {"EHV": [], "HV": [], "MV": [], "LV": []}

        for root, _, files in os.walk(self.base_folder):
            for file in files:
                if not file.lower().endswith(".json"):
                    continue
                full_path = os.path.join(root, file)
                print(f"Lade {file}: Datei einlesen…")

                # JSON laden und in Pandapower-Netz konvertieren
                pp_net = pp.from_json(full_path)

                # Mittelwert von vn_kv im Bus-DF berechnen
                vn_values = pp_net.bus["vn_kv"].tolist()
                mean_vn = sum(vn_values) / len(vn_values) if vn_values else 0.0
                print(f"  gefundene vn_kv-Werte = {vn_values}")
                print(f"  ⇒ mittlerer vn_kv = {mean_vn:.3f}")

                # Ebene auf Basis von mean_vn bestimmen
                if mean_vn > 50:
                    level = "EHV"
                elif mean_vn > 20:
                    level = "HV"
                elif mean_vn > 5:  
                    level = "MV"
                else:
                    level = "LV"
                print(f"  ⇒ {file} wird als {level} erkannt (mean vn_kv = {mean_vn:.3f})")

                # In Network umwandeln
                net_obj = Network.from_pandapower(pp_net)
                result[level].append(net_obj)

        return result