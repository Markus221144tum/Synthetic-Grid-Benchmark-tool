import pandas as pd
from real_vs_synth.metrics.topological_characteristics import (
    compute_node_degree_metrics,
    compute_clustering_coefficient,
    compute_characteristic_path_length,
    compute_graph_diameter,
    compute_betweenness_centrality
)

from real_vs_synth.metrics.system_characteristics import compute_system_metrics
from real_vs_synth.viz.plt_comparison import plot_topological_comparison, plot_system_metrics


class Comparer:

    def compare(self, real_nets: dict, synth_nets: dict) -> pd.DataFrame:
        rows = []
        for level in ['MV', 'LV']:
            real_list = real_nets.get(level, [])
            synth_list = synth_nets.get(level, [])
            if not real_list or not synth_list:
                continue

            # Knotengrad (Real & Synth)
            real_degs = [compute_node_degree_metrics(n)[0] for n in real_list]
            real_mean_deg = sum(real_degs) / len(real_degs)
            synth_degs = [compute_node_degree_metrics(n)[0] for n in synth_list]
            synth_mean_deg = sum(synth_degs) / len(synth_degs)

            # Clustering Coeff (Real & Synth)
            real_ccs = [compute_clustering_coefficient(n)[0] for n in real_list]
            real_mean_cc = sum(real_ccs) / len(real_ccs)
            synth_ccs = [compute_clustering_coefficient(n)[0] for n in synth_list]
            synth_mean_cc = sum(synth_ccs) / len(synth_ccs)

            # Characteristic Path Length (Real & Synth)
            real_cpls = [compute_characteristic_path_length(n)[0] for n in real_list]
            real_mean_cpl = sum(real_cpls) / len(real_cpls)
            synth_cpls = [compute_characteristic_path_length(n)[0] for n in synth_list]
            synth_mean_cpl = sum(synth_cpls) / len(synth_cpls)

            # Graph Diameter (Real & Synth)
            real_diams = [compute_graph_diameter(n) for n in real_list]
            real_diameter = sum(real_diams) / len(real_diams)
            synth_diams = [compute_graph_diameter(n) for n in synth_list]
            synth_diameter = sum(synth_diams) / len(synth_diams)

            # Betweenness Centrality (Real & Synth)
            real_bws = [compute_betweenness_centrality(n)[0] for n in real_list]
            real_mean_bw = sum(real_bws) / len(real_bws)
            synth_bws = [compute_betweenness_centrality(n)[0] for n in synth_list]
            synth_mean_bw = sum(synth_bws) / len(synth_bws)

            rows.append({
                'level': level,
                'real_mean_deg': real_mean_deg,
                'synth_mean_deg': synth_mean_deg,
                'deg_diff': real_mean_deg - synth_mean_deg,
                'real_mean_cc': real_mean_cc,
                'synth_mean_cc': synth_mean_cc,
                'cc_diff': real_mean_cc - synth_mean_cc,
                'real_mean_cpl': real_mean_cpl,
                'synth_mean_cpl': synth_mean_cpl,
                'cpl_diff': real_mean_cpl - synth_mean_cpl,
                'real_diameter': real_diameter,
                'synth_diameter': synth_diameter,
                'diam_diff': real_diameter - synth_diameter,
                'real_mean_bw': real_mean_bw,
                'synth_mean_bw': synth_mean_bw,
                'bw_diff': real_mean_bw - synth_mean_bw
            })

        return pd.DataFrame(rows)

    def compare_system_metrics(self, networks: dict, label: str) -> list:
        return [compute_system_metrics(net) for net in networks.get('MV', []) + networks.get('LV', [])]

    def plot_system_metrics(self, real_nets: dict, synth_nets: dict):
        real_metrics = self.compare_system_metrics(real_nets, "Real")
        synth_metrics = self.compare_system_metrics(synth_nets, "Synthetic")
        labels = ["Real"] * len(real_metrics) + ["Synthetic"] * len(synth_metrics)
        metrics = real_metrics + synth_metrics
        plot_system_metrics(metrics, labels)
