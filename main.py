import argparse
import os
from real_vs_synth.data.simbench_loader import SimBenchLoader
from real_vs_synth.data.synthetic_loader import SyntheticLoader
from real_vs_synth.data.cvs_loader import CsvLoader
from real_vs_synth.analysis.comparer import Comparer
from real_vs_synth.viz.plt_comparison import plot_topological_comparison

def main():
    parser = argparse.ArgumentParser(
        description="Compare topological metrics between Real and Synthetic power networks"
    )
    parser.add_argument(
        '--real', required=True,
        help="Pfad zu Real-Netz-Daten (SimBench-Kennungen oder Verzeichnis mit JSON/CSV)"
    )
    parser.add_argument(
        '--synthetic', required=True,
        help="Pfad zu Synthetic-Netz-Daten (Verzeichnis mit JSON oder CSV)"
    )
    args = parser.parse_args()

    # --- Lade reale Netze ---
    real_path = args.real
    if os.path.isdir(real_path):
        print("Lade Real-Netze aus Verzeichnis als CSV/JSON …")
        has_bus_csv = any(
            os.path.isdir(os.path.join(real_path, d)) and
            os.path.exists(os.path.join(real_path, d, 'bus.csv'))
            for d in os.listdir(real_path)
        )
        real_loader = CsvLoader(real_path) if has_bus_csv else SyntheticLoader(real_path)
    else:
        print("Lade Real-Netze über SimBenchLoader …")
        real_loader = SimBenchLoader()
    real_networks = real_loader.load(real_path)

    # --- Lade synthetische Netze ---
    synth_path = args.synthetic
    if os.path.isdir(synth_path):
        print("Lade Synthetic-Netze aus JSON-Verzeichnis …")
        synth_loader = SyntheticLoader(synth_path)
    else:
        print("Lade Synthetic-Netze über CSV-Loader …")
        synth_loader = CsvLoader(synth_path)
    synthetic_networks = synth_loader.load(synth_path)

    print(f"Reale Netz-Level: {list(real_networks.keys())}")
    for lvl, nets in real_networks.items():
        print(f"  -> {lvl}: {len(nets)} Netz(e)")

    print(f"Anzahl synthetischer Netze: {sum(len(v) for v in synthetic_networks.values())}")

    # --- Vergleiche Real vs. Synthetic ---
    comparer = Comparer()
    df = comparer.compare(real_networks, synthetic_networks)
    print("Ergebnisse (metrische Vergleiche):")
    print(df.to_string(index=False))

    # --- Visualisiere die Ergebnisse ---
    print("Zeige Balkendiagramm für alle Topo-Metriken …")
    plot_topological_comparison(df)

    # --- Visualisiere systemische Metriken ---
    print("Zeige Balkendiagramm für System-Metriken …")
    comparer.plot_system_metrics(real_networks, synthetic_networks)

if __name__ == '__main__':
    main()


#python main.py --real "real_vs_synth/data/1-LV-rural1--1-no_sw/train"  --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"
#python main.py --real simbench  --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"