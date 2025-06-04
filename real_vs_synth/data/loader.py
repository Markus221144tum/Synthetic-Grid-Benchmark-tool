from .simbench_loader import SimBenchLoader
from .csvs_loader import CsvLoader
from .synthetic_loader import SyntheticLoader

def get_loader(path: str):
    """
    Hilfsfunktion, um automatisch anhand des Pfades zu entscheiden,
    welcher Loader (SimBenchLoader, CsvLoader oder SyntheticLoader) verwendet wird.
    """
    import os
    if os.path.isdir(path):
        # Prüfen, ob Unterordner CSV-Dateien (bus.csv) enthalten
        has_bus_csv = any(
            os.path.isdir(os.path.join(path, d)) and
            os.path.exists(os.path.join(path, d, "bus.csv"))
            for d in os.listdir(path)
        )
        if has_bus_csv:
            return CsvLoader(path)
        else:
            return SyntheticLoader(path)
    else:
        # Kein Verzeichnis → wir gehen von SimBench-Kennung aus
        return SimBenchLoader()