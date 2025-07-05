import simbench as sb
from multiprocessing import Pool, cpu_count
from real_vs_synth.model.network import Network

# Mappings für Regionen
REGION_MAP = {"r": "rural", "m": "mixed", "c": "urban", "u": "urban", "s": "semiurb", "comm": "comm"}

# Alle SimBench-Codes, strukturiert nach Ebene und Region
SIMBENCH_CODES = {
    "EHV": [("1-EHV-mixed--0-sw", "mixed")],
    "HV": [
        ("1-HV-mixed--0-sw", "mixed"),
        ("1-HV-urban--0-sw", "urban")
    ],
    "MV": [
        ("1-MV-rural--0-sw", "rural"),
        ("1-MV-semiurb--0-sw", "mixed"),
        ("1-MV-urban--0-sw", "urban"),
        ("1-MV-comm--0-sw", "comm")
    ],
    "LV": [
        ("1-LV-rural1--0-sw", "rural"),
        ("1-LV-rural2--0-sw", "rural"),
        ("1-LV-rural3--0-sw", "rural"),
        ("1-LV-semiurb4--0-sw", "mixed"),
        ("1-LV-semiurb5--0-sw", "mixed"),
        ("1-LV-urban6--0-sw", "urban")
    ]
}

def load_simbench_net(code_level_tuple):
    code, level = code_level_tuple
    net = sb.get_simbench_net(code)
    net_obj = Network.from_pandapower(net)
    return (level, net_obj, code)

class SimBenchLoader:
    """
    Lädt SimBench-Netze für alle Spannungsebenen, optional gefiltert nach Region/Level.
    Gibt Konsolenausgabe für jeden geladenen Code.
    """

    def load(self, path: str = None, level_filter=None, region_filter=None) -> dict:
        """
        Optional: level_filter = 'LV'/'MV'/'HV'/'EHV' (str oder Liste)
                  region_filter = 'r'/'m'/'c'/... (siehe REGION_MAP, str oder Liste)
        """
        result = {"EHV": [], "HV": [], "MV": [], "LV": []}
        code_level = []

        # Filter auflisten:
        level_filter = [level_filter] if isinstance(level_filter, str) else level_filter
        region_filter = [region_filter] if isinstance(region_filter, str) else region_filter

        for level, code_region_pairs in SIMBENCH_CODES.items():
            if level_filter and level not in level_filter:
                continue
            for code, region in code_region_pairs:
                # Region filtern
                if region_filter:
                    # Kürzel umsetzen
                    region_long = [REGION_MAP.get(r, r) for r in region_filter]
                    if region not in region_long:
                        continue
                code_level.append((code, level))

        with Pool(min(cpu_count(), 8)) as pool:
            loaded = pool.map(load_simbench_net, code_level)
        for level, net_obj, code in loaded:
            result[level].append(net_obj)
            print(f"  ⇒ SimBench-Code {code} wird als {level} geladen.")
        return result