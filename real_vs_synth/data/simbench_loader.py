import simbench as sb
from real_vs_synth.model.network import Network

class SimBenchLoader:
    """
    Lädt SimBench-Netze für alle Spannungsebenen (EHV/HV/MV/LV).
    """

    def load(self, path: str = None) -> dict:
        """
        Ignoriert den Parameter path und lädt statisch alle Ebenen:
        EHV, HV, MV, LV. Gibt ein Dict {"EHV":[Network], "HV":[...], ...} zurück.
        """
        result = {"EHV": [], "HV": [], "MV": [], "LV": []}

        # 1. EHV
        sb_code_ehv = "1-EHV-mixed--0-sw"
        net_ehv = sb.get_simbench_net(sb_code_ehv)
        result["EHV"].append(Network.from_pandapower(net_ehv))

        # 2. HV
        hv_codes = ["1-HV-mixed--0-sw", "1-HV-urban--0-sw"]
        for code in hv_codes:
            net = sb.get_simbench_net(code)
            result["HV"].append(Network.from_pandapower(net))

        # 3. MV
        mv_codes = [
            "1-MV-rural--0-sw", "1-MV-semiurb--0-sw",
            "1-MV-urban--0-sw", "1-MV-comm--0-sw"
        ]
        for code in mv_codes:
            net = sb.get_simbench_net(code)
            result["MV"].append(Network.from_pandapower(net))

        # 4. LV
        lv_codes = [
            "1-LV-rural1--0-sw", "1-LV-rural2--0-sw", "1-LV-rural3--0-sw",
            "1-LV-semiurb4--0-sw", "1-LV-semiurb5--0-sw", "1-LV-urban6--0-sw"
        ]
        for code in lv_codes:
            net = sb.get_simbench_net(code)
            result["LV"].append(Network.from_pandapower(net))

        return result