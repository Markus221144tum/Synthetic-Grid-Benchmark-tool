import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_topological_comparison(df):
    """
    Erwartet ein DataFrame mit Spalten:
      ['level', 'real_mean_deg', 'synth_mean_deg', 'deg_diff',
       'real_mean_cc', 'synth_mean_cc', 'cc_diff',
       'real_mean_cpl', 'synth_mean_cpl', 'cpl_diff',
       'real_diameter', 'synth_diameter', 'diam_diff',
       'real_mean_bw', 'synth_mean_bw', 'bw_diff']

    Zeichnet separate Balkendiagramme für jede Metrik:
      1) Mean Node Degree
      2) Mean Clustering Coefficient
      3) Mean Characteristic Path Length
      4) Graph Diameter
      5) Mean Betweenness Centrality
    """
    levels = df['level'].values
    x = np.arange(len(levels))
    width = 0.35

    fig, axs = plt.subplots(5, 1, figsize=(8, 20))

    # 1) Node Degree
    axs[0].bar(x - width/2, df['real_mean_deg'], width, label='Real', color='blue')
    axs[0].bar(x + width/2, df['synth_mean_deg'], width, label='Synthetic', color='orange')
    axs[0].set_ylabel('Mean Node Degree')
    axs[0].set_title('Comparison: Node Degree')
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(levels)
    axs[0].legend()

    # 2) Clustering Coefficient
    axs[1].bar(x - width/2, df['real_mean_cc'], width, label='Real', color='blue')
    axs[1].bar(x + width/2, df['synth_mean_cc'], width, label='Synthetic', color='orange')
    axs[1].set_ylabel('Mean Clustering Coeff.')
    axs[1].set_title('Comparison: Clustering Coefficient')
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(levels)
    axs[1].legend()

    # 3) Characteristic Path Length
    axs[2].bar(x - width/2, df['real_mean_cpl'], width, label='Real', color='blue')
    axs[2].bar(x + width/2, df['synth_mean_cpl'], width, label='Synthetic', color='orange')
    axs[2].set_ylabel('Mean Path Length')
    axs[2].set_title('Comparison: Characteristic Path Length')
    axs[2].set_xticks(x)
    axs[2].set_xticklabels(levels)
    axs[2].legend()

    # 4) Graph Diameter
    axs[3].bar(x - width/2, df['real_diameter'], width, label='Real', color='blue')
    axs[3].bar(x + width/2, df['synth_diameter'], width, label='Synthetic', color='orange')
    axs[3].set_ylabel('Diameter')
    axs[3].set_title('Comparison: Graph Diameter')
    axs[3].set_xticks(x)
    axs[3].set_xticklabels(levels)
    axs[3].legend()

    # 5) Betweenness Centrality
    axs[4].bar(x - width/2, df['real_mean_bw'], width, label='Real', color='blue')
    axs[4].bar(x + width/2, df['synth_mean_bw'], width, label='Synthetic', color='orange')
    axs[4].set_ylabel('Mean Betweenness')
    axs[4].set_title('Comparison: Betweenness Centrality')
    axs[4].set_xticks(x)
    axs[4].set_xticklabels(levels)
    axs[4].legend()

    plt.tight_layout()
    plt.show()
    
def plot_system_metrics(metrics_list: list[dict], labels: list[str]):
    if not metrics_list:
        print("Keine Systemmetriken zur Anzeige verfügbar.")
        return

    df = pd.DataFrame(metrics_list)
    df['label'] = labels

    for col in df.columns:
        if col == 'label':
            continue
        fig, ax = plt.subplots()
        df.boxplot(column=col, by='label', ax=ax)
        ax.set_title(f'Systemmetrik: {col}')
        ax.set_xlabel('Datensatz')
        ax.set_ylabel(col)
        plt.suptitle('')
        plt.tight_layout()
        plt.show()
