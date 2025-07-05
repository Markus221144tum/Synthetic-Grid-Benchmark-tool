import pandas as pd
import json
import os
from real_vs_synth.metrics.topological_characteristics import (
    compute_node_degree_metrics,
    compute_clustering_coefficient,
    compute_characteristic_path_length,
    compute_graph_diameter,
    compute_betweenness_centrality,
    compute_meshness,                
    compute_degree_assortativity     
)
from real_vs_synth.metrics.system_characteristics import compute_system_metrics
from real_vs_synth.viz.plt_comparison import (
    plot_topological_comparison,
    plot_system_metrics
)

class Comparer:

    def compare(self, real_nets: dict, synth_nets: dict) -> pd.DataFrame:
        rows = []
        distributions = {}

        for level in ['MV', 'LV']:
            real_list = real_nets.get(level, [])
            synth_list = synth_nets.get(level, [])
            if not real_list or not synth_list:
                continue

            distributions[level] = {
                'real': {'deg': [], 'cc': [], 'cpl': [], 'bw': [], 'mesh': [], 'assort': []},
                'synth': {'deg': [], 'cc': [], 'cpl': [], 'bw': [], 'mesh': [], 'assort': []}
            }

            # Topologische Metriken berechnen
            real_deg = [compute_node_degree_metrics(n) for n in real_list]
            synth_deg = [compute_node_degree_metrics(n) for n in synth_list]
            real_cc = [compute_clustering_coefficient(n) for n in real_list]
            synth_cc = [compute_clustering_coefficient(n) for n in synth_list]
            real_cpl = [compute_characteristic_path_length(n) for n in real_list]
            synth_cpl = [compute_characteristic_path_length(n) for n in synth_list]
            real_diams = [compute_graph_diameter(n)[0] for n in real_list]
            synth_diams = [compute_graph_diameter(n)[0] for n in synth_list]
            real_bw = [compute_betweenness_centrality(n) for n in real_list]
            synth_bw = [compute_betweenness_centrality(n) for n in synth_list]

            # NEU: Meshness (Vermaschtheitsgrad) & Degree Assortativity
            real_mesh = [compute_meshness(n) for n in real_list]
            synth_mesh = [compute_meshness(n) for n in synth_list]
            real_assort = [compute_degree_assortativity(n) for n in real_list]
            synth_assort = [compute_degree_assortativity(n) for n in synth_list]

            # Verteilungen extrahieren
            for d in real_deg: distributions[level]['real']['deg'].extend(d[2])
            for d in synth_deg: distributions[level]['synth']['deg'].extend(d[2])
            for d in real_cc: distributions[level]['real']['cc'].extend(d[2])
            for d in synth_cc: distributions[level]['synth']['cc'].extend(d[2])
            for d in real_cpl: distributions[level]['real']['cpl'].extend(d[2])
            for d in synth_cpl: distributions[level]['synth']['cpl'].extend(d[2])
            for d in real_bw: distributions[level]['real']['bw'].extend(d[2])
            for d in synth_bw: distributions[level]['synth']['bw'].extend(d[2])
            distributions[level]['real']['mesh'] = real_mesh
            distributions[level]['synth']['mesh'] = synth_mesh
            distributions[level]['real']['assort'] = real_assort
            distributions[level]['synth']['assort'] = synth_assort
            distributions[level]['real']['diameter'] = real_diams
            distributions[level]['synth']['diameter'] = synth_diams
            distributions[level]['real']['diameter'] = real_diams
            distributions[level]['synth']['diameter'] = synth_diams

            # Zeile für DataFrame (inkl. NEUER METRIKEN)
            row = {
                'level': level,
                'real_mean_deg': sum(d[0] for d in real_deg) / len(real_deg),
                'synth_mean_deg': sum(d[0] for d in synth_deg) / len(synth_deg),
                'deg_diff': (sum(d[0] for d in real_deg) - sum(d[0] for d in synth_deg)) / len(real_deg),

                'real_mean_cc': sum(d[0] for d in real_cc) / len(real_cc),
                'synth_mean_cc': sum(d[0] for d in synth_cc) / len(synth_cc),
                'cc_diff': (sum(d[0] for d in real_cc) - sum(d[0] for d in synth_cc)) / len(real_cc),

                'real_mean_cpl': sum(d[0] for d in real_cpl) / len(real_cpl),
                'synth_mean_cpl': sum(d[0] for d in synth_cpl) / len(synth_cpl),
                'cpl_diff': (sum(d[0] for d in real_cpl) - sum(d[0] for d in synth_cpl)) / len(real_cpl),

                'real_mean_diameter': sum(real_diams) / len(real_diams),
                'synth_mean_diameter': sum(synth_diams) / len(synth_diams),
                'diam_diff': (sum(real_diams) - sum(synth_diams)) / len(real_diams),

                'real_mean_bw': sum(d[0] for d in real_bw) / len(real_bw),
                'synth_mean_bw': sum(d[0] for d in synth_bw) / len(synth_bw),
                'bw_diff': (sum(d[0] for d in real_bw) - sum(d[0] for d in synth_bw)) / len(real_bw),

                'real_mean_mesh': sum(real_mesh) / len(real_mesh),
                'synth_mean_mesh': sum(synth_mesh) / len(synth_mesh),
                'mesh_diff': (sum(real_mesh) - sum(synth_mesh)) / len(real_mesh),

                'real_mean_assort': sum(real_assort) / len(real_assort),
                'synth_mean_assort': sum(synth_assort) / len(synth_assort),
                'assort_diff': (sum(real_assort) - sum(synth_assort)) / len(real_assort),

                # Verteilungen für Boxplots etc.
                'real_deg_distrib': distributions[level]['real']['deg'],
                'synth_deg_distrib': distributions[level]['synth']['deg'],
                'real_cc_distrib': distributions[level]['real']['cc'],
                'synth_cc_distrib': distributions[level]['synth']['cc'],
                'real_cpl_distrib': distributions[level]['real']['cpl'],
                'synth_cpl_distrib': distributions[level]['synth']['cpl'],
                'real_bw_distrib': distributions[level]['real']['bw'],
                'synth_bw_distrib': distributions[level]['synth']['bw'],
                'real_mesh_distrib': distributions[level]['real']['mesh'],
                'synth_mesh_distrib': distributions[level]['synth']['mesh'],
                'real_assort_distrib': distributions[level]['real']['assort'],
                'synth_assort_distrib': distributions[level]['synth']['assort'],
                'real_diameter_distrib': distributions[level]['real']['diameter'],
                'synth_diameter_distrib': distributions[level]['synth']['diameter']
            }
            rows.append(row)

        # JSON speichern
        with open("topological_distributions.json", "w") as f:
            json.dump(distributions, f, indent=2)

        df = pd.DataFrame(rows)
        # plot_topological_comparison(df)  # Optionaler Plot
        return df

    def compare_system_metrics(self, networks: dict, label: str) -> list:
        return [compute_system_metrics(net) for net in networks.get('MV', []) + networks.get('LV', [])]

    def plot_system_metrics(self, real_nets: dict, synth_nets: dict):
        real_metrics = self.compare_system_metrics(real_nets, "Real")
        synth_metrics = self.compare_system_metrics(synth_nets, "Synthetic")
        labels = ["Real"] * len(real_metrics) + ["Synthetic"] * len(synth_metrics)
        metrics = real_metrics + synth_metrics
        plot_system_metrics(metrics, labels)
