import argparse
import os
from real_vs_synth.data.simbench_loader import SimBenchLoader
from real_vs_synth.data.synthetic_loader import SyntheticLoader
from real_vs_synth.data.cvs_loader import CsvLoader
from real_vs_synth.data.dingo_loader import DingoLoader
from real_vs_synth.analysis.comparer import Comparer
from real_vs_synth.viz.plt_comparison import plot_topological_comparison
import pandapower.plotting as plot
from real_vs_synth.data.pt_loader import PtLoader
from real_vs_synth.viz.plt_comparison import (
    plot_topo_hist_distributions,
    plot_system_hist_distributions
)

    
def visualize_all_networks(networks, title_prefix=""):
    for level, nets in networks.items():
        for i, net in enumerate(nets):
            try:
                print(f"Plot: {title_prefix} Ebene {level}, Netz {i+1}")
                if hasattr(net, "pp_net"):  # Pandapower Netz
                    plot.simple_plot(net.pp_net)

                elif hasattr(net, "edge_index") and hasattr(net, "num_nodes"):
                    # PyTorch Geometric Netz als NetworkX zeichnen
                    from torch_geometric.utils import to_networkx
                    import networkx as nx
                    import matplotlib.pyplot as plt

                    G_nx = to_networkx(net, to_undirected=True)
                    plt.figure(figsize=(6, 6))
                    nx.draw(G_nx, node_size=30, with_labels=False)
                    plt.title(f"{title_prefix} {level} Netz {i+1}")
                    plt.show()

                elif isinstance(net, dict) and "edge_index" in net and "num_nodes" in net:
                    # .pt Format geladen als dict (z. B. torch.load())
                    import torch
                    import networkx as nx
                    from torch_geometric.data import Data
                    from torch_geometric.utils import to_networkx
                    import matplotlib.pyplot as plt

                    data = Data(edge_index=net["edge_index"], num_nodes=net["num_nodes"])
                    G_nx = to_networkx(data, to_undirected=True)
                    plt.figure(figsize=(6, 6))
                    nx.draw(G_nx, node_size=30, with_labels=False)
                    plt.title(f"{title_prefix} {level} Netz {i+1}")
                    plt.show()

                else:
                    print(f"Nicht unterstützter Netztyp für {title_prefix} {level} Netz {i+1}")

            except Exception as e:
                print(f"Plot nicht möglich für {title_prefix} {level} Netz {i+1}: {e}")
  

def select_loader(path: str):
    if path.lower().startswith("simbench"):
        return SimBenchLoader(), True
    if os.path.isdir(path):
        has_bus_csv = any(
            os.path.isdir(os.path.join(path, d)) and
            os.path.exists(os.path.join(path, d, 'bus.csv'))
            for d in os.listdir(path)
        )
        if has_bus_csv:
            return CsvLoader(path), False
        elif any(f.endswith(".pt") for f in os.listdir(path)):
            return PtLoader(path), False
        else:
            return SyntheticLoader(path), False
    elif path.lower().endswith('.pkl'):
        print(f"Lade Netze aus Dingo-PKL-Datei: {path}")
        return DingoLoader(os.path.dirname(path)), False
    else:
        return SimBenchLoader(), True

def main():
    parser = argparse.ArgumentParser(
        description="Compare topological and system metrics between Real and Synthetic power networks"
    )
    parser.add_argument('--real', required=True,
                        help="Pfad zu Real-Netz-Daten (simbench für SimBench, sonst Pfad)")
    parser.add_argument('--synthetic', required=True,
                        help="Pfad zu Synthetic-Netz-Daten (simbench für SimBench, sonst Pfad)")
    parser.add_argument('--real_level', type=str, default=None,
                        help="Filter für reale Spannungsebene: LV, MV, HV, EHV (nur für simbench)")
    parser.add_argument('--real_region', type=str, default=None,
                        help="Region real: r (rural), m (mixed), c (city/urban), s (semiurb), comm (nur für simbench)")
    parser.add_argument('--synthetic_level', type=str, default=None,
                        help="Filter für synthetische Spannungsebene: LV, MV, HV, EHV (nur für simbench)")
    parser.add_argument('--synthetic_region', type=str, default=None,
                        help="Region synthetic: r (rural), m (mixed), c (city/urban), s (semiurb), comm (nur für simbench)")
    parser.add_argument('--export_json', action='store_true',
                        help="Speichert statistische Verteilungen und Mittelwerte als JSON-Datei im ./results Verzeichnis")
    args = parser.parse_args()

    # Lade reale Netze (SimBench-Filter nur falls gewünscht)
    real_loader, real_is_simbench = select_loader(args.real)
    if real_is_simbench:
        real_networks = real_loader.load(level_filter=args.real_level, region_filter=args.real_region)
    else:
        real_networks = real_loader.load(args.real)

    # Lade synthetische Netze (SimBench-Filter nur falls gewünscht)
    synth_loader, synth_is_simbench = select_loader(args.synthetic)
    if synth_is_simbench:
        synthetic_networks = synth_loader.load(level_filter=args.synthetic_level, region_filter=args.synthetic_region)
    else:
        synthetic_networks = synth_loader.load(args.synthetic)

    print(f"Reale Netz-Level: {list(real_networks.keys())}")
    for lvl, nets in real_networks.items():
        print(f"  -> {lvl}: {len(nets)} Netz(e)")

    print(f"Anzahl synthetischer Netze: {sum(len(v) for v in synthetic_networks.values())}")
    
    #Visualisierung der Netze zum Überprüfen
    # bei Großen Daten unbedingt Deaktivieren
  
    # Visualisierung für reale Netze
    visualize_all_networks(real_networks, title_prefix="Reales")
    
    # Visualisierung für synthetische Netze
    visualize_all_networks(synthetic_networks, title_prefix="Synthetisch")
    
    # Vergleiche Real vs. Synthetic
    comparer = Comparer()
    df = comparer.compare(real_networks, synthetic_networks)
    print("Ergebnisse (metrische Vergleiche):")
    #print(df.to_string(index=False))
    
    print("Zeige Balkendiagramm für alle Topo-Metriken …")
    plot_topological_comparison(df)
    
    print("Zeige Balkendiagramm für System-Metriken …")
    comparer.plot_system_metrics(real_networks, synthetic_networks)
    
    # Histogramm-Plot für Topologie
    plot_topo_hist_distributions(df)
    
    # Histogramm-Plot für Systemmetriken
    real_metrics = comparer.compare_system_metrics(real_networks, "Real")
    synth_metrics = comparer.compare_system_metrics(synthetic_networks, "Synthetic")
    plot_system_hist_distributions(real_metrics + synth_metrics, ["Real"] * len(real_metrics) + ["Synthetic"] * len(synth_metrics))
    
    #if args.export_json:
    #print("Exportiere Verteilungen als JSON …")
    #comparer.export_statistics_to_json(real_networks, synthetic_networks, output_dir="results")

if __name__ == '__main__':
    main()

# Beispielaufrufe:
# Alle SimBench-Netze:        
#   python main.py --real simbench --synthetic simbench
# Nur LV rural gegen LV urban:
#   python main.py --real simbench --real_level LV --real_region m --synthetic simbench --synthetic_level LV --synthetic_region c
# HV mixed vs. HV mixed:
#   python main.py --real simbench --real_level HV --real_region m --synthetic simbench --synthetic_level HV --synthetic_region m

# Beispielaufrufe zur Nutzung des Skripts:
# python main.py --real "real_vs_synth/data/1-LV-rural1--1-no_sw/train" --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"
# python main.py --real simbench --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"
# python main.py --real "real_vs_synth/data/dingo_grids_1-100" --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"
# python main.py --real "real_vs_synth/data/1-LV-rural1--1-no_sw/train" --synthetic "real_vs_synth/data/dingo_grids_3601-3608"

# python main.py --real "real_vs_synth/data/generated_nets" --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"