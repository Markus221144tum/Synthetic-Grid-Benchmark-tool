import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_topological_comparison(df):
    """
    Zeigt zwei separate Visualisierungen:
    1. Balkendiagramme der Mittelwerte
    2. Boxplots der Verteilungen
    Falls eine Metrik nur Nullen enthält, wird sie ausgelassen und unten aufgeführt.
    """
    levels = df['level'].values
    x = np.arange(len(levels))
    width = 0.35
    skipped_metrics = []

    # --- 1. Mittelwerte als Balkendiagramme ---
    metric_map = {
        'deg': 'Mean Node Degree',
        'cc': 'Clustering Coefficient',
        'cpl': 'Path Length',
        'diameter': 'Graph Diameter',
        'bw': 'Betweenness Centrality'
    }

    plot_keys = []
    for key in metric_map:
        real = df.get(f'real_mean_{key}', [])
        synth = df.get(f'synth_mean_{key}', [])
        if len(real) == 0 or (all(v == 0 for v in real) and all(v == 0 for v in synth)):
            skipped_metrics.append(metric_map[key])
            continue
        plot_keys.append(key)

    fig1, axs1 = plt.subplots(1, len(plot_keys), figsize=(6 * len(plot_keys), 6))
    if len(plot_keys) == 1:
        axs1 = [axs1]

    for ax, key in zip(axs1, plot_keys):
        ax.bar(x - width/2, df[f'real_mean_{key}'], width, label='Real', color='blue')
        ax.bar(x + width/2, df[f'synth_mean_{key}'], width, label='Synthetic', color='orange')
        ax.set_title(metric_map[key])
        ax.set_xticks(x)
        ax.set_xticklabels(levels)
        ax.legend()

    fig1.suptitle('Topological Metrics - Mean Values')
    plt.tight_layout(pad=3.0)
    plt.subplots_adjust(top=0.85)
    plt.show()

    # --- 2. Boxplots der Verteilungen ---
    fig2, axs2 = plt.subplots(1, len(plot_keys), figsize=(6 * len(plot_keys), 6))
    if len(plot_keys) == 1:
        axs2 = [axs2]

    for ax, key in zip(axs2, plot_keys):
        real_vals = df.iloc[0][f'real_{key}_distrib']
        synth_vals = df.iloc[0][f'synth_{key}_distrib']
        ax.boxplot([real_vals, synth_vals], labels=['Real', 'Synthetic'])
        ax.set_title(f'{metric_map[key]} (Boxplot)')

    fig2.suptitle('Topological Metrics - Distributions (Boxplots)')
    plt.tight_layout(pad=3.0)
    plt.subplots_adjust(top=0.85)
    if skipped_metrics:
        print("Folgende Topo-Metriken wurden ausgelassen (nur Nullwerte):")
        for m in skipped_metrics:
            print(f" - {m}")
    plt.show()

def plot_system_metrics(metrics_list: list[dict], labels: list[str]):
    """
    Zeigt zwei Darstellungen der Systemmetriken:
    1. Balkendiagramme der Mittelwerte
    2. Boxplots der Verteilungen
    Wenn eine Metrik nur Nullen enthält, wird sie ausgelassen und unten aufgeführt.
    """
    if not metrics_list:
        print("Keine Systemmetriken zur Anzeige verfügbar.")
        return

    df = pd.DataFrame(metrics_list)
    df['label'] = labels
    numeric_cols = [col for col in df.columns if col != 'label' and pd.api.types.is_numeric_dtype(df[col])]

    skipped_metrics = []

    # --- 1. Mittelwerte ---
    means = df.groupby('label')[numeric_cols].mean()
    kept_cols = [col for col in means.columns if not all(df[col] == 0)]
    skipped_metrics.extend([col for col in means.columns if all(df[col] == 0)])

    fig1, axs1 = plt.subplots(nrows=(len(kept_cols) - 1) // 5 + 1, ncols=5, figsize=(5 * min(5, len(kept_cols)), 6))
    axs1 = axs1.flatten() if isinstance(axs1, np.ndarray) else [axs1]

    for i, col in enumerate(kept_cols):
        axs1[i].bar(means.index, means[col], color=['blue', 'orange'])
        axs1[i].set_title(col)
        axs1[i].set_ylabel(col)
        axs1[i].tick_params(axis='x', rotation=45)
    for j in range(len(kept_cols), len(axs1)):
        axs1[j].axis('off')

    plt.tight_layout(pad=3.0)
    plt.suptitle('Systemmetriken: Mittelwerte', fontsize=16)
    plt.subplots_adjust(top=0.92)
    plt.show()

    # --- 2. Boxplots ---
    fig2, axs2 = plt.subplots(nrows=(len(kept_cols) - 1) // 5 + 1, ncols=5, figsize=(5 * min(5, len(kept_cols)), 6))
    axs2 = axs2.flatten() if isinstance(axs2, np.ndarray) else [axs2]

    for i, col in enumerate(kept_cols):
        df.boxplot(column=col, by='label', ax=axs2[i])
        axs2[i].set_title(col)
        axs2[i].set_xlabel('')
        axs2[i].tick_params(axis='x', rotation=45)
    for j in range(len(kept_cols), len(axs2)):
        axs2[j].axis('off')

    plt.tight_layout(pad=3.0)
    plt.suptitle('Systemmetriken: Verteilungen (Boxplots)', fontsize=16)
    plt.subplots_adjust(top=0.92)
    if skipped_metrics:
        print("Folgende Systemmetriken wurden ausgelassen (nur Nullwerte):")
        for m in skipped_metrics:
            print(f" - {m}")
    plt.show()
