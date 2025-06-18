Hier ist dein überarbeitetes und stilistisch verbesserter **README-Text** auf Englisch, formatiert als Fließtext – alle Informationen und dein Stil wurden beibehalten, aber sprachlich klarer und professioneller ausformuliert:

---

# Synthetic Grid Benchmark Tool

The purpose of this codebase is to provide a tool that compares two grid datasets and computes a set of metrics to evaluate which dataset is more realistic or representative. This tool can be used with official **SimBench** datasets or your own grid models based on **pandapower**. The results are visualized through graphs and stored in a structured JSON file for further analysis or integration.

Currently, the comparison includes two complementary layers:

1. **Topological properties** – Graph-theoretical metrics derived from the network structure, independent of electrical parameters.
2. **System properties** – Metrics related to physical infrastructure and electrical operation of the grid.

The code is modular and extensible. Additional metric categories and analysis layers can be easily integrated.

---

### Project Structure

The folder layout is organized as follows:

```
main.py                              # Main entry point via command line
real_vs_synth/
├── analysis/
│   └── comparer.py                  # Coordinates metric calculation and visualizations
├── data/
│   ├── cvs_loader.py                # Loader for pandapower CSV datasets
│   ├── simbench_loader.py           # Automatic loader for SimBench codes
│   └── synthetic_loader.py          # Loader for JSON-based pandapower models
├── metrics/
│   ├── topological_characteristics.py  # Implements graph-based metrics
│   └── system_characteristics.py       # Extracts electrical infrastructure stats
├── model/
│   └── network.py                   # Wrapper for combining pandapower with NetworkX
└── viz/
    └── plt_comparison.py           # Plotting functions (bar charts, box plots)
README.md                           # This documentation
```

---

### Data Handling

SimBench datasets are downloaded automatically using the API.
To include your own data, simply copy the dataset folders into the project directory. If the datasets are large, the comparison may take some time to compute (the example folder only contains 10 test networks for speed).

---

## System Requirements

All required packages and versions are listed in the `requirements.txt` file.
To recreate the exact environment:

```bash
pip install -r requirements.txt
```

---

## Quick Start – Command Line Examples

To compare two datasets, use the following CLI commands:

1. Compare two folders that both contain LV JSON grid models:

```bash
python main.py --real "real_vs_synth/data/1-LV-rural1--1-no_sw/train" --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"
```

2. Use the official SimBench dataset as your "real" benchmark, and compare it against your own local JSON/CSV models:

```bash
python main.py --real simbench --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"
```

The terms "real" and "synthetic" are merely semantic – they help distinguish the two input sets. You can freely assign any datasets to either side, regardless of size or source. The loader automatically identifies the data format and voltage level.

---

## How the Code Works

1. **Loading and Normalization**

   The tool detects whether the supplied input is:

   * a **SimBench code**
   * a directory with **CSV files** (pandapower export)
   * a directory with **JSON-based pandapower networks**

   The voltage level is inferred from the attribute `bus.vn_kv` and categorized as Extra-HV, HV, MV, or LV.

2. **Network Representation**

   Each pandapower grid is transformed into a **NetworkX MultiGraph**.
   For topological analysis, multi-edges are collapsed into a **simple undirected graph**. (here may are some problems, where I'am still checking)

3. **Metric Computation**

   * **Topological Metrics:**

     | Metric                     | Description                        | Output Format                |
     | -------------------------- | ---------------------------------- | ---------------------------- |
     | Node degree                | Number of direct neighbors         | Mean, std, full distribution |
     | Clustering coefficient     | Ratio of closed triangles          | Mean, std, distribution      |
     | Characteristic path length | Avg. shortest-path length          | Mean + full distance list    |
     | Diameter                   | Longest shortest path in the graph | Single value                 |
     | Betweenness centrality     | Shortest-path node participation   | Mean, std, distribution      |

   * **System Metrics:**

     * Total line length, line length per customer and per km²
     * Share of overhead vs. underground lines
     * Number of transformers, average kVA, average X/R ratio
     * Load: Total active/reactive power, power factor, load per customer
     * Generation: PV, wind, other, and total installed capacity
     * Customers per transformer

   Each metric is calculated twice:

   * Mean value for bar charts
   * Value distribution across networks for box plots

4. **Results and Output**

   * A structured summary is saved as `metrics_summary.json` in `real_vs_synth/results/`
   * Two additional files – `topological_distributions.json` and `system_distributions.json` – are created for storing the raw distributions (useful for post-processing)

5. **Visualization**

   The tool generates four main plots:

   * **Figure 1:** Topological metrics (mean values – bar plots)
   * **Figure 2:** Topological metrics (distributions – box plots)
   * **Figure 3:** System metrics (mean values – bar plots)
   * **Figure 4:** System metrics (distributions – box plots)

   If a metric is zero across all networks (e.g., no generators present), the respective subplot is **omitted**, and the metric is listed below the plot instead. Remaining plots automatically reflow to use space efficiently.

---

## Interpreting the Output

* **Colors**: Real networks are shown in **blue**, synthetic in **orange**.
* **Bar Chart Gaps**: A large difference between real and synthetic in the bar plots often indicates a mismatch in grid realism.
* **Box Plot Separation**: Non-overlapping boxplots suggest systematic differences in the network properties.
* **Missing Metrics**: The console output will notify if certain metrics were skipped due to all-zero values:

  ```text
  Skipped system metrics (all values zero):
  - pv_kw
  - wind_kw
  ```

  This might mean that your models lack these elements, which is fine.

---

## Extending the Tool

* **Add custom metrics**: Implement a new function in `metrics/`, import it in `comparer.py`, and visualize it in `plt_comparison.py`.
* **Support more formats**: Create a loader in `data/` that returns a dictionary `{'LV': [...], 'MV': [...], ...}` of networks.
* **Run headless**: Replace all `plt.show()` calls with `plt.savefig()` to automatically generate reports without GUI.

---

## Support


Happy benchmarking! ⚡

