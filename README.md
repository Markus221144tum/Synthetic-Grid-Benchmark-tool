# Synthetic-Grid-Benchmark-tool

The goal of this code os to build a tool, wich compares two grid-datasets and generate matrics, which describes the quality of those datasets to decide, which is the more realistic Dataset. To do that,you can use the Simbench dataset or your owne panda-power based datasets. The results are showen i grapes and in a Jason data, for further use.

The comparison covers yet two complementary layers:

1. Topological properties – pure graph-theoretic metrics, independent of electrical parameters.
2. System properties – electrical and infrastructure statistics that describe how a grid is built and operated.

The code is build modular, so further layers and matrics can be added easily.




### 1 · Folder Structure 



├── main.py                      		 		  # single entry point (CLI)
├── real_vs_synth
│   ├── analysis
│   │   └── comparer.py         				  # manages metric calculation + plotting
│   ├── data
│   │   ├── cvs_loader.py	  					# loader for CVS Datasets
│   │   └── simbench_loader.py					# loader for simbench
│   │   └── synthetic_loader.py					# loader for pandapower based Jason datasets
│   ├── metrics
│   │   ├── topological_characteristics.py	  # math für the topological metrics
│   │   └── system_characteristics.py		
│   ├── model
│   │   └── network.py            					# tiny wrapper: pandapower ↔ NetworkX
│   └── viz
│       └── plt_comparison.py     					# matplotlib helpers (bar & box plots)
└── README.md                    				



### Data handle

The simbench datasets will bei downloaded automatically via the api. 
To include other datasets, just copy the folder in to the "Code" folder and run the code. If the datasets are large, it will compute a while. (that is the reason, why the test dataset only contains 10 grid examples)



## 2 · System Requirements

For the requirements, read the "Requirements.txt"

---

## 3 · Quick Start – CLI Examples


1) Compare two folders that both contain LV JSON networks

python main.py \ --real "real_vs_synth/data/1-LV-rural1--1-no_sw/train" \ --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"



2) Use the official SimBench data set as “real” and your local JSON/CSV files as “synthetic”

python main.py \ --real simbench \ --synthetic "real_vs_synth/data/1-LV-rural1--1-no_sw/train"
  

The name "real" and "synthetic" is just a seperation. It is easier to handle than "dataset 1 and dataset 2". you can insert every dataset here, with any size. The loader works automaticly and the voltage level will be automaticly selected.


## 4 How does the code work?

1. **Load & normalise the networks**

   * The loader detects whether the supplied path is a *SimBench code*, a directory that contains **CSV folders** (pandapower export), or a directory that contains **JSON models**.
   * Voltage levels are derived from `bus.vn_kv` and categorised into Extra-HV, HV, MV or LV.

2. **Build a NetworkX graph**

   * Every pandapower element is translated into an undirected multi-graph.
   * For topological metrics we internally collapse parallel edges to obtain a simple graph.

3. **Compute metrics**

   **Topology**

   | Metric                     | Description                            | Output                       |
   | -------------------------- | -------------------------------------- | ---------------------------- |
   | Node degree                | direct neighbours of each node         | mean, std, full distribution |
   | Clustering coefficient     | local closed-triangle ratio            | mean, std, distribution      |
   | Characteristic path length | avg. shortest-path distance            | mean & list of all *dᵢⱼ*     |
   | Diameter                   | longest shortest path                  | single value                 |
   | Betweenness centrality     | how often a node is on a shortest path | mean, std, distribution      |

   **System**

   * Global cable length, length per customer and per km²
   * Overhead vs. underground share
   * Transformer count, mean kVA, mean X/R
   * Load: P & Q totals, P per customer, power factor
   * Generation: PV, wind, other, totals
   * Customers per transformer

   Each metric is delivered **twice**:

   * an *aggregate* number, also the mean (for bar charts)
   * the *standard distribution* across networks (for box plots)

4. **Persist results**

   * A `metrics_summary.json` under `real_vs_synth/results/` (auto-created) will be created for further use
   * Two separate JSONs (`topological_distributions.json`, `system_distributions.json`) if you want to post-process the raw lists.

5. **Visualise**

   The plotting helper produces four panels with multible graphes:

   
   Figure 1   Topology · means      (bars)
   Figure 2   Topology · distributions (boxplots)
   Figure 3   System   · means      (bars)
   Figure 4   System   · distributions (boxplots)
  

   If every value of a metric is zero (e.g. your models contain no generators yet), the corresponding subplot is removed, and the metric name is appended    to a plain-text list that is printed below the figure, so Removed plots do not leave blank space – surviving plots slide together automatically.




## 5 · Interpreting the Output

* **Blue vs. Orange** – by default, *Real = blue*, *Synthetic = orange*.
  Large deviations in the bar charts or non-overlapping boxplots usually pinpoint where a synthetic generator struggles to mimic reality.

* **Missing metrics** – the console prints lines like

  ```
  Skipped system metrics (all values zero):
  - pv_kw
  - wind_kw
  ```

  Add the corresponding data columns to your pandapower model or ignore if those assets are genuinely absent.

* **Voltage levels** – everything is aggregated per level (MV, LV, …). Extend `comparer.py` if you need per-network granularity.

---

## 6 · Extending the Tool

* **Add new metrics** – drop a function in `metrics/…`, import it in `comparer.py`, append plotting logic in `plt_comparison.py`.
* **Use another file format** – implement a loader in `real_vs_synth/data/`, return a `dict[str, list[Network]]` with keys `EHV/HV/MV/LV`.
* **Headless mode** – replace `plt.show()` with `plt.savefig()` if you need automated reporting.

---

## 7 · Support

Feel free to open an issue or contact the author if you run into problems, want to contribute a pull-request, or simply discuss synthetic grid modelling.

Happy benchmarking! ⚡
